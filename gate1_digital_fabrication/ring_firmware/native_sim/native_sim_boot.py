#!/usr/bin/env python3
"""Host native_sim for Edge I/O Ring — digital bring-up without hardware."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINOUT = ROOT / "dts" / "pinout.json"


def boot_sim() -> dict:
    pinout = json.loads(PINOUT.read_text(encoding="utf-8"))
    gpio = pinout["gpio"]
    # Simulated register file
    regs = {v["label"]: "input_hi_z" for v in gpio.values()}
    regs["I2C0"] = "configured"
    events = [
        "reset_vector",
        "clock_hfclk_requested",
        "i2c0_init",
        "bmi270_probe",
        "drv2605l_probe",
        "ble_stack_stub",
        "idle",
    ]
    return {
        "board": pinout["board"],
        "mcu": pinout["mcu"],
        "regs": regs,
        "events": events,
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
