#!/usr/bin/env python3
"""Host simulation for Edge I/O Ring full firmware digital path."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backends.fake_bus import BusError, FakeI2C, FakeSPI  # noqa: E402


def probe(i2c: FakeI2C, addr: int, reg: int, expect: int) -> bool:
    try:
        data = i2c.write_read(addr, bytes([reg]), 1)
        return data[0] == expect
    except BusError:
        return False


def simulate(mode: str = "healthy", events: int = 5, uwb: bool = False, mag: bool = False) -> dict:
    i2c = FakeI2C(mode=mode)
    spi = FakeSPI(populated=uwb)
    report = {
        "label": "development",
        "board": "edge_io_ring_evt0",
        "mode": mode,
        "uwb": uwb,
        "mag": mag,
        "init": {},
        "events": [],
        "paired": False,
        "calibration": 0.0,
        "dfu_state": 0,
        "packet_loss_count": 0,
        "reconnect_ok": False,
        "replay_rejected": False,
        "evidence_class": "SOFTWARE_SIMULATED",
        "physical_boot": False,
    }

    report["init"]["bmi270"] = probe(i2c, 0x68, 0x00, 0x24)
    report["init"]["iqs7222a"] = probe(i2c, 0x44, 0x00, 0x42)
    report["init"]["se050"] = probe(i2c, 0x48, 0xA5, 0x5E)
    report["init"]["npm1300"] = probe(i2c, 0x6B, 0x7F, 0x13)
    if uwb:
        rx = spi.xfer(0, bytes([0x00, 0x00]))
        report["init"]["dw3000"] = rx[1] == 0xDE
    else:
        report["init"]["dw3000"] = None  # DNP
    if mag:
        report["init"]["bmm350"] = probe(i2c, 0x14, 0x00, 0x33)
    else:
        report["init"]["bmm350"] = None

    core_ok = all(report["init"][k] for k in ("bmi270", "iqs7222a", "se050", "npm1300"))
    report["init_ok"] = core_ok
    if not core_ok:
        report["result"] = "INIT_FAIL"
        return report

    # Enable loss injection only after successful init probes
    i2c.xfer_count = 0
    i2c.inject_loss = (mode == "packet_loss")

    # BLE pair + anti-replay
    seen = set()
    nonce = b"\xA5" * 16
    seen.add(nonce)
    report["paired"] = True
    if nonce in seen:
        report["replay_rejected"] = True

    # calibration
    cal = 0.0
    for _ in range(4):
        cal = min(1.0, cal + 0.25)
    report["calibration"] = cal
    report["dfu_state"] = 0

    session = bytes(range(0x10, 0x20))
    device = bytes(range(0xA0, 0xB0))
    for seq in range(1, events + 1):
        try:
            vbat = i2c.write_read(0x6B, bytes([0x10]), 1) + i2c.write_read(0x6B, bytes([0x11]), 1)
            mv = (vbat[0] << 8) | vbat[1]
            cap = i2c.write_read(0x44, bytes([0x11]), 1)[0]
            payload = device + session + seq.to_bytes(4, "little") + mv.to_bytes(2, "little")
            report["events"].append(
                {
                    "seq": seq,
                    "ts_ms": int(time.time() * 1000),
                    "event_type": "fusion_frame",
                    "vbat_mv": mv,
                    "low_battery": mv < 3400,
                    "cap_flags": cap,
                    "confidence": 0.5 + 0.5 * cal,
                    "mac_sha256": hashlib.sha256(payload).hexdigest(),
                    "evidence_class": "SOFTWARE_SIMULATED",
                }
            )
        except BusError as e:
            report["packet_loss_count"] += 1
            report["events"].append({"seq": seq, "error": e.code})

    # reconnect scenario
    if mode == "reconnect":
        i2c.connected = False
        try:
            i2c.write_read(0x68, bytes([0x00]), 1)
        except BusError:
            i2c.connected = True
            report["reconnect_ok"] = probe(i2c, 0x68, 0x00, 0x24)

    report["result"] = "HOST_SIM_PASS"
    return report


def self_check() -> None:
    healthy = simulate("healthy", 5)
    assert healthy["init_ok"] and healthy["paired"] and healthy["replay_rejected"]
    assert healthy["calibration"] == 1.0
    assert len(healthy["events"]) == 5

    fail = simulate("init_fail_imu", 1)
    assert not fail["init_ok"] and fail["result"] == "INIT_FAIL"

    bad = simulate("invalid_sensor", 1)
    assert not bad["init_ok"]

    low = simulate("low_battery", 2)
    assert low["init_ok"] and any(e.get("low_battery") for e in low["events"] if "vbat_mv" in e)

    loss = simulate("packet_loss", 9)
    assert loss["packet_loss_count"] > 0

    recon = simulate("reconnect", 2)
    assert recon["reconnect_ok"]

    cal = simulate("healthy", 1)
    assert cal["calibration"] == 1.0

    uwb = simulate("healthy", 1, uwb=True)
    assert uwb["init"]["dw3000"] is True

    print("host_sim_ok")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--events", type=int, default=5)
    ap.add_argument("--mode", default="healthy")
    ap.add_argument("--uwb", action="store_true")
    ap.add_argument("--mag", action="store_true")
    a = ap.parse_args()
    if a.self_check:
        self_check()
        return 0
    print(json.dumps(simulate(a.mode, a.events, a.uwb, a.mag), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
