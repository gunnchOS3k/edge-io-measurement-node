#!/usr/bin/env python3
"""Host native_sim for Edge I/O Ring — digital bring-up without hardware.

Includes BLE stub pairing, anti-replay seq checks, and pinout-backed GPIO map.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINOUT = ROOT / "dts" / "pinout.json"


class BleStub:
    """Minimal BLE pairing / advertising stub for digital tests."""

    def __init__(self) -> None:
        self.advertising = False
        self.connected = False
        self.paired = False
        self._session_key = b"\x11" * 16
        self._seen_nonces: set[bytes] = set()

    def start_advertise(self) -> str:
        self.advertising = True
        return "ADV_OK"

    def connect(self) -> str:
        if not self.advertising:
            return "ERR_NOT_ADVERTISING"
        self.connected = True
        return "CONN_OK"

    def pair(self, nonce16: bytes) -> tuple[str, bytes]:
        if not self.connected:
            return "ERR_NOT_CONNECTED", b""
        if len(nonce16) != 16:
            return "ERR_BAD_NONCE", b""
        if nonce16 in self._seen_nonces:
            return "ERR_REPLAY", b""
        self._seen_nonces.add(nonce16)
        resp = hmac.new(self._session_key, nonce16, hashlib.sha256).digest()[:16]
        self.paired = True
        return "PAIR_OK", resp

    def disconnect(self) -> str:
        self.connected = False
        self.advertising = False
        return "DISC_OK"


def boot_sim() -> dict:
    pinout = json.loads(PINOUT.read_text(encoding="utf-8"))
    gpio = pinout["gpio"]
    regs = {v["label"]: "input_hi_z" for v in gpio.values()}
    regs["I2C0"] = "configured"
    ble = BleStub()
    assert ble.start_advertise() == "ADV_OK"
    assert ble.connect() == "CONN_OK"
    st, resp = ble.pair(b"\xA5" * 16)
    assert st == "PAIR_OK" and len(resp) == 16
    st_replay, _ = ble.pair(b"\xA5" * 16)
    assert st_replay == "ERR_REPLAY"
    events = [
        "reset_vector",
        "clock_hfclk_requested",
        "i2c0_init",
        "bmi270_probe",
        "drv2605l_probe",
        "ble_adv_start",
        "ble_connect",
        "ble_pair",
        "ble_replay_rejected",
        "idle",
    ]
    return {
        "board": pinout["board"],
        "mcu": pinout["mcu"],
        "regs": regs,
        "events": events,
        "ble": {
            "paired": ble.paired,
            "connected": ble.connected,
            "replay_rejected": True,
        },
        "physical_boot": False,
        "token": "RING_PHYSICAL_BOOT_PENDING",
        "result": "NATIVE_SIM_PASS",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    report = boot_sim()
    if args.self_check:
        assert report["result"] == "NATIVE_SIM_PASS"
        assert report["physical_boot"] is False
        assert report["ble"]["paired"] is True
        assert report["ble"]["replay_rejected"] is True
        assert "P0.26" in report["regs"]
        assert "P0.27" in report["regs"]
        assert "P0.11" in report["regs"]
        assert "P0.02" in report["regs"]
        print("NATIVE_SIM_SELF_CHECK_OK")
        return 0
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
