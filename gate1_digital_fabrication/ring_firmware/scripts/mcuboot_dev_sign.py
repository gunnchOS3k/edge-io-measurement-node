#!/usr/bin/env python3
"""MCUboot-like DEVELOPMENT image signing (HMAC-SHA256 envelope).

DEVELOPMENT keys only. Not a claim of on-device MCUboot boot.
Produces signed image + tampered negative fixtures.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import pathlib
import shutil
import sys

MAGIC = b"GCHMCU1\0"
ROOT = pathlib.Path(__file__).resolve().parents[1]


def verify(blob: bytes, key: bytes) -> bool:
    if len(blob) < len(MAGIC) + 32:
        return False
    body, tag = blob[:-32], blob[-32:]
    if not body.startswith(MAGIC):
        return False
    expect = hmac.new(key, body, hashlib.sha256).digest()
    return hmac.compare_digest(expect, tag)


def sign(bin_path: pathlib.Path, key_path: pathlib.Path, out_dir: pathlib.Path) -> dict:
    payload = bin_path.read_bytes()
    key = key_path.read_bytes()
    body = MAGIC + payload
    digest = hmac.new(key, body, hashlib.sha256).digest()
    out_dir.mkdir(parents=True, exist_ok=True)
    fixtures = ROOT / "mcuboot" / "fixtures"
    fixtures.mkdir(parents=True, exist_ok=True)

    signed_bytes = body + digest
    signed = out_dir / "ring_firmware_mcuboot_signed_dev.bin"
    signed.write_bytes(signed_bytes)
    shutil.copyfile(signed, out_dir / "slot0_image_signed_dev.bin")
    (out_dir / "mcuboot").mkdir(exist_ok=True)
    (out_dir / "mcuboot" / "ring_firmware_dev_signed.bin").write_bytes(signed_bytes)

    neg = []

    # Payload tamper
    t_payload = bytearray(signed_bytes)
    if len(payload) > 0:
        t_payload[len(MAGIC) + len(payload) - 1] ^= 0xFF
    p1 = out_dir / "ring_firmware_dev_TAMPERED.bin"
    p1.write_bytes(bytes(t_payload))
    (out_dir / "mcuboot" / "ring_firmware_dev_TAMPERED.bin").write_bytes(bytes(t_payload))
    (fixtures / "tampered_payload.bin").write_bytes(bytes(t_payload))
    neg.append(
        {
            "name": "tampered_payload",
            "path": str(fixtures / "tampered_payload.bin"),
            "expect": "VERIFY_FAIL",
            "verified": verify(bytes(t_payload), key),
            "ok": not verify(bytes(t_payload), key),
        }
    )

    # Signature tamper
    t_sig = bytearray(signed_bytes)
    t_sig[-1] ^= 0xFF
    (fixtures / "tampered_signature.bin").write_bytes(bytes(t_sig))
    neg.append(
        {
            "name": "tampered_signature",
            "path": str(fixtures / "tampered_signature.bin"),
            "expect": "VERIFY_FAIL",
            "verified": verify(bytes(t_sig), key),
            "ok": not verify(bytes(t_sig), key),
        }
    )

    # Truncated
    t_trunc = signed_bytes[: len(MAGIC) + 8]
    (fixtures / "truncated_image.bin").write_bytes(t_trunc)
    neg.append(
        {
            "name": "truncated_image",
            "path": str(fixtures / "truncated_image.bin"),
            "expect": "VERIFY_FAIL",
            "verified": verify(t_trunc, key),
            "ok": not verify(t_trunc, key),
        }
    )

    # Bad magic
    t_magic = bytearray(signed_bytes)
    t_magic[0:8] = b"BADMAGIC"
    (fixtures / "bad_magic.bin").write_bytes(bytes(t_magic))
    neg.append(
        {
            "name": "bad_magic",
            "path": str(fixtures / "bad_magic.bin"),
            "expect": "VERIFY_FAIL",
            "verified": verify(bytes(t_magic), key),
            "ok": not verify(bytes(t_magic), key),
        }
    )

    (fixtures / "NEGATIVE_FIXTURES.json").write_text(json.dumps(neg, indent=2) + "\n", encoding="utf-8")

    ok = verify(signed.read_bytes(), key)
    bad = verify(p1.read_bytes(), key)
    if not all(f["ok"] for f in neg):
        raise SystemExit("negative fixture unexpectedly verified")

    meta = {
        "signed": signed.name,
        "tampered": p1.name,
        "verify_signed_ok": ok,
        "verify_tampered_ok": bad,
        "verify_positive": ok,
        "key_label": "DEVELOPMENT_ONLY",
        "key_class": "DEVELOPMENT",
        "physical_boot_claim": False,
        "physical_boot_claimed": False,
        "tokens": [
            "RING_MCU_TARGET_FIRMWARE_BUILD_PASS",
            "RING_PHYSICAL_BOOT_PENDING",
        ],
        "status_tokens": [
            "RING_MCU_TARGET_FIRMWARE_BUILD_PASS",
            "RING_PHYSICAL_BOOT_PENDING",
        ],
        "negative_fixtures": neg,
    }
    report = out_dir / "MCUBOOT_SIGN_REPORT.json"
    report.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (out_dir / "mcuboot" / "mcuboot_dev_sign_report.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    if not ok or bad:
        raise SystemExit("signing verification contract failed")
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
    meta = sign(bin_path, pathlib.Path(args.key), pathlib.Path(args.out))
    print("MCUBOOT_DEVELOPMENT_SIGN_PASS")
    print("RING_PHYSICAL_BOOT_PENDING")
    print("MCUBOOT_DEV_SIGN_OK", json.dumps({k: meta[k] for k in ("signed", "verify_positive", "key_class")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
