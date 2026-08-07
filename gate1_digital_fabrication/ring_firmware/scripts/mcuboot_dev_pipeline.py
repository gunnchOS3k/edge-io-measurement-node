#!/usr/bin/env python3
"""MCUboot DEVELOPMENT pipeline: sign / update / revert / factory-test / anti-replay.

DEVELOPMENT HMAC-SHA256 envelopes only. Not on-device MCUboot. No physical boot claim.
Token on success: RING_MCUBOOT_DEV_PIPELINE_PASS
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import pathlib
import struct
import sys

MAGIC = b"GCHMCU1\0"
HDR_FMT = "<8sII16s"  # magic, image_version, anti_replay_counter, image_kind
KIND_SLOT0 = b"slot0\0\0\0\0\0\0\0"
KIND_UPDATE = b"update\0\0\0\0\0\0"
KIND_REVERT = b"revert\0\0\0\0\0\0"
KIND_FACTORY = b"factory\0\0\0\0\0"

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _kind_pad(s: bytes) -> bytes:
    return (s + b"\0" * 16)[:16]


def verify(blob: bytes, key: bytes) -> bool:
    if len(blob) < 32 + 32:  # header min + tag; header is 32 bytes
        return False
    body, tag = blob[:-32], blob[-32:]
    if not body.startswith(MAGIC):
        return False
    expect = hmac.new(key, body, hashlib.sha256).digest()
    return hmac.compare_digest(expect, tag)


def parse_header(blob: bytes) -> dict | None:
    if len(blob) < 32 or not blob.startswith(MAGIC):
        return None
    magic, ver, counter, kind = struct.unpack(HDR_FMT, blob[:32])
    return {
        "magic": magic.rstrip(b"\0").decode("latin1"),
        "image_version": ver,
        "anti_replay_counter": counter,
        "image_kind": kind.rstrip(b"\0").decode("ascii", errors="replace"),
    }


def pack_body(payload: bytes, version: int, counter: int, kind: bytes) -> bytes:
    hdr = struct.pack(HDR_FMT, MAGIC, version, counter, _kind_pad(kind))
    return hdr + payload


def sign_body(body: bytes, key: bytes) -> bytes:
    return body + hmac.new(key, body, hashlib.sha256).digest()


def anti_replay_accept(seen: set[int], counter: int) -> bool:
    """Reject replayed counters; accept strictly increasing."""
    if counter in seen:
        return False
    if seen and counter <= max(seen):
        return False
    seen.add(counter)
    return True


def build_pipeline(bin_path: pathlib.Path, key_path: pathlib.Path, out_dir: pathlib.Path) -> dict:
    payload = bin_path.read_bytes()
    key = key_path.read_bytes()
    out_dir.mkdir(parents=True, exist_ok=True)
    pipe = out_dir / "mcuboot_pipeline"
    pipe.mkdir(parents=True, exist_ok=True)
    fixtures = ROOT / "mcuboot" / "fixtures"
    fixtures.mkdir(parents=True, exist_ok=True)
    pipeline_fixtures = fixtures / "pipeline"
    pipeline_fixtures.mkdir(parents=True, exist_ok=True)

    # Slot0 signed (v1, counter=1)
    slot0_body = pack_body(payload, version=1, counter=1, kind=KIND_SLOT0)
    slot0 = sign_body(slot0_body, key)
    (pipe / "slot0_signed_dev.bin").write_bytes(slot0)
    (out_dir / "ring_firmware_mcuboot_signed_dev.bin").write_bytes(slot0)
    (out_dir / "slot0_image_signed_dev.bin").write_bytes(slot0)
    (out_dir / "mcuboot").mkdir(exist_ok=True)
    (out_dir / "mcuboot" / "ring_firmware_dev_signed.bin").write_bytes(slot0)

    # Update image for slot1 (v2, counter=2)
    update_body = pack_body(payload + b"\x01", version=2, counter=2, kind=KIND_UPDATE)
    update = sign_body(update_body, key)
    (pipe / "slot1_update_signed_dev.bin").write_bytes(update)
    (pipeline_fixtures / "slot1_update_signed_dev.bin").write_bytes(update)

    # Revert package: prior slot0 + revert marker (v1, counter=3) — counter advances on revert too
    revert_body = pack_body(payload, version=1, counter=3, kind=KIND_REVERT)
    revert = sign_body(revert_body, key)
    (pipe / "revert_signed_dev.bin").write_bytes(revert)
    (pipeline_fixtures / "revert_signed_dev.bin").write_bytes(revert)

    # Factory-test fixture (v0 factory, counter=100)
    factory_payload = b"FACTORY_SELFTEST_V0\n" + payload[:64]
    factory_body = pack_body(factory_payload, version=0, counter=100, kind=KIND_FACTORY)
    factory = sign_body(factory_body, key)
    (pipe / "factory_test_signed_dev.bin").write_bytes(factory)
    (pipeline_fixtures / "factory_test_signed_dev.bin").write_bytes(factory)

    # Negative / anti-replay fixtures
    neg: list[dict] = []

    # Tampered update payload
    t_upd = bytearray(update)
    t_upd[40] ^= 0xFF
    (pipeline_fixtures / "tampered_update.bin").write_bytes(bytes(t_upd))
    neg.append(
        {
            "name": "tampered_update",
            "expect": "VERIFY_FAIL",
            "verified": verify(bytes(t_upd), key),
            "ok": not verify(bytes(t_upd), key),
        }
    )

    # Replay of slot0 counter after update accepted (isolated counter set)
    replay_seen: set[int] = set()
    assert anti_replay_accept(replay_seen, 1)
    assert anti_replay_accept(replay_seen, 2)
    replay_ok = anti_replay_accept(replay_seen, 1)  # should reject
    (pipeline_fixtures / "replay_slot0_counter.bin").write_bytes(slot0)
    neg.append(
        {
            "name": "anti_replay_reject_counter_1",
            "expect": "REPLAY_REJECT",
            "verified": verify(slot0, key),  # signature still valid
            "replay_accepted": replay_ok,
            "ok": (not replay_ok) and verify(slot0, key),
        }
    )

    # Truncated update
    trunc = update[:20]
    (pipeline_fixtures / "truncated_update.bin").write_bytes(trunc)
    neg.append(
        {
            "name": "truncated_update",
            "expect": "VERIFY_FAIL",
            "verified": verify(trunc, key),
            "ok": not verify(trunc, key),
        }
    )

    # Also keep classic negatives for compatibility
    t_payload = bytearray(slot0)
    t_payload[len(slot0) - 40] ^= 0xFF
    (fixtures / "tampered_payload.bin").write_bytes(bytes(t_payload))
    t_sig = bytearray(slot0)
    t_sig[-1] ^= 0xFF
    (fixtures / "tampered_signature.bin").write_bytes(bytes(t_sig))
    t_trunc = slot0[:16]
    (fixtures / "truncated_image.bin").write_bytes(t_trunc)
    t_magic = bytearray(slot0)
    t_magic[0:8] = b"BADMAGIC"
    (fixtures / "bad_magic.bin").write_bytes(bytes(t_magic))
    classic = [
        {"name": "tampered_payload", "expect": "VERIFY_FAIL", "verified": verify(bytes(t_payload), key), "ok": not verify(bytes(t_payload), key)},
        {"name": "tampered_signature", "expect": "VERIFY_FAIL", "verified": verify(bytes(t_sig), key), "ok": not verify(bytes(t_sig), key)},
        {"name": "truncated_image", "expect": "VERIFY_FAIL", "verified": verify(t_trunc, key), "ok": not verify(t_trunc, key)},
        {"name": "bad_magic", "expect": "VERIFY_FAIL", "verified": verify(bytes(t_magic), key), "ok": not verify(bytes(t_magic), key)},
    ]
    (fixtures / "NEGATIVE_FIXTURES.json").write_text(json.dumps(classic, indent=2) + "\n", encoding="utf-8")

    # Swap / update / revert digital state machine (host-side)
    seen: set[int] = set()
    state = {
        "active_slot": "slot0",
        "pending": None,
        "confirmed": True,
        "anti_replay_seen": [],
    }
    # Confirm slot0 then simulate update → pending slot1
    assert verify(slot0, key)
    hdr0 = parse_header(slot0)
    assert hdr0 and anti_replay_accept(seen, hdr0["anti_replay_counter"])
    assert verify(update, key)
    hdr_u = parse_header(update)
    assert hdr_u and anti_replay_accept(seen, hdr_u["anti_replay_counter"])
    state["pending"] = "slot1"
    state["confirmed"] = False
    state["active_slot"] = "slot1"  # test-boot into update
    # Revert
    assert verify(revert, key)
    hdr_r = parse_header(revert)
    assert hdr_r and anti_replay_accept(seen, hdr_r["anti_replay_counter"])
    state["active_slot"] = "slot0"
    state["pending"] = None
    state["confirmed"] = True
    state["anti_replay_seen"] = sorted(seen)
    (pipe / "swap_state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    (pipeline_fixtures / "swap_state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    assert verify(slot0, key)
    assert verify(update, key)
    assert verify(revert, key)
    assert verify(factory, key)
    assert all(f["ok"] for f in neg)
    assert all(f["ok"] for f in classic)

    meta = {
        "pipeline": "sign/update/revert/factory-test/anti-replay",
        "key_label": "DEVELOPMENT_ONLY",
        "key_class": "DEVELOPMENT",
        "physical_boot_claim": False,
        "physical_boot_claimed": False,
        "verify_slot0": True,
        "verify_update": True,
        "verify_revert": True,
        "verify_factory": True,
        "anti_replay_ok": True,
        "swap_state": state,
        "artifacts": {
            "slot0": "mcuboot_pipeline/slot0_signed_dev.bin",
            "update": "mcuboot_pipeline/slot1_update_signed_dev.bin",
            "revert": "mcuboot_pipeline/revert_signed_dev.bin",
            "factory": "mcuboot_pipeline/factory_test_signed_dev.bin",
        },
        "headers": {
            "slot0": parse_header(slot0),
            "update": parse_header(update),
            "revert": parse_header(revert),
            "factory": parse_header(factory),
        },
        "negative_fixtures": neg,
        "classic_negatives": classic,
        "tokens": [
            "RING_MCUBOOT_DEV_PIPELINE_PASS",
            "RING_MCU_TARGET_FIRMWARE_BUILD_PASS",
            "RING_PHYSICAL_BOOT_PENDING",
        ],
        "status_tokens": [
            "RING_MCUBOOT_DEV_PIPELINE_PASS",
            "RING_MCU_TARGET_FIRMWARE_BUILD_PASS",
            "RING_PHYSICAL_BOOT_PENDING",
        ],
        # legacy fields for older tests
        "signed": "ring_firmware_mcuboot_signed_dev.bin",
        "tampered": "tampered_payload.bin",
        "verify_signed_ok": True,
        "verify_tampered_ok": False,
        "verify_positive": True,
    }
    # Sanitize headers already JSON-safe via parse_header
    report_path = out_dir / "MCUBOOT_SIGN_REPORT.json"
    report_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (out_dir / "MCUBOOT_PIPELINE_REPORT.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (out_dir / "mcuboot" / "mcuboot_dev_sign_report.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (pipe / "pipeline_report.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (pipeline_fixtures / "PIPELINE_FIXTURES.json").write_text(
        json.dumps({"negatives": neg, "swap_state": state}, indent=2) + "\n", encoding="utf-8"
    )
    return meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", default=str(ROOT / "build/out/ring_firmware_release_development.bin"))
    ap.add_argument("--key", default=str(ROOT / "mcuboot/dev_keys/development.key"))
    ap.add_argument("--out", default=str(ROOT / "build/out"))
    args = ap.parse_args()
    bin_path = pathlib.Path(args.bin)
    if not bin_path.exists():
        alt = ROOT / "build/out/ring_firmware_dev.bin"
        if alt.exists():
            bin_path = alt
        else:
            raise SystemExit(f"missing firmware bin: {bin_path}")
    meta = build_pipeline(bin_path, pathlib.Path(args.key), pathlib.Path(args.out))
    print("MCUBOOT_DEVELOPMENT_SIGN_PASS")
    print("RING_MCUBOOT_DEV_PIPELINE_PASS")
    print("RING_PHYSICAL_BOOT_PENDING")
    print(
        "MCUBOOT_DEV_PIPELINE_OK",
        json.dumps(
            {
                k: meta[k]
                for k in (
                    "verify_slot0",
                    "verify_update",
                    "verify_revert",
                    "verify_factory",
                    "anti_replay_ok",
                    "key_class",
                )
            }
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
