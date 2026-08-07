#!/usr/bin/env python3
"""Lightweight static analysis for ring firmware digital closure.

Checks source shape, forbidden physical-boot claims, pinout consistency, and basic hygiene.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "out"

FORBIDDEN_CLAIM_PATTERNS = [
    re.compile(r"PHYSICAL_BOOT_PASS", re.I),
    re.compile(r"RING_PHYSICAL_BOOT_PASS", re.I),
    re.compile(r"flashed\s+to\s+hardware", re.I),
    re.compile(r"on-device\s+boot\s+verified", re.I),
]

REQUIRED_FILES = [
    "src/ring_fw.c",
    "src/ring_fw_freestanding.c",
    "src/startup_arm.c",
    "include/ring_fw.h",
    "boards/arm/edge_io_ring/board.h",
    "dts/edge_io_ring.dts",
    "dts/pinout.json",
]


def main() -> int:
    findings: list[dict] = []
    for rel in REQUIRED_FILES:
        p = ROOT / rel
        if not p.exists():
            findings.append({"severity": "error", "file": rel, "msg": "missing required file"})

    # Scan text sources for forbidden physical-boot success claims
    skip_names = {"static_analysis.py"}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.name in skip_names:
            continue
        if any(part in {".toolchain", "build", ".pytest_cache", "__pycache__", ".git"} for part in path.parts):
            continue
        if path.suffix.lower() not in {".c", ".h", ".py", ".md", ".dts", ".yml", ".yaml", ".json", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pat in FORBIDDEN_CLAIM_PATTERNS:
            if pat.search(text):
                findings.append(
                    {
                        "severity": "error",
                        "file": str(path.relative_to(ROOT)),
                        "msg": f"forbidden claim pattern: {pat.pattern}",
                    }
                )

    # Pinout consistency board.h ↔ pinout.json
    pinout = json.loads((ROOT / "dts" / "pinout.json").read_text(encoding="utf-8"))
    board_h = (ROOT / "boards" / "arm" / "edge_io_ring" / "board.h").read_text(encoding="utf-8")
    mapping = {
        "I2C_SDA": "RING_PIN_I2C_SDA",
        "I2C_SCL": "RING_PIN_I2C_SCL",
        "IMU_INT": "RING_PIN_IMU_INT",
        "CHG_STATUS": "RING_PIN_CHG_STATUS",
    }
    for net, macro in mapping.items():
        pin = pinout["gpio"][net]["pin"]
        m = re.search(rf"#define\s+{macro}\s+(\d+)", board_h)
        if not m or int(m.group(1)) != pin:
            findings.append({"severity": "error", "file": "board.h/pinout", "msg": f"mismatch {net}"})

    dts = (ROOT / "dts" / "edge_io_ring.dts").read_text(encoding="utf-8")
    for needle in ("bmi270@68", "drv2605l@5a", "gpios = <&gpio0 11 0>", "gpios = <&gpio0 2 0>", "P0.26", "P0.27"):
        if needle not in dts and needle.replace("P0.", "") not in dts:
            # P0.26 encoded as comment/psels — tolerate comment form
            if "0.26" not in dts and "26" not in dts and needle.startswith("P0"):
                findings.append({"severity": "error", "file": "dts/edge_io_ring.dts", "msg": f"missing {needle}"})
            elif not needle.startswith("P0"):
                findings.append({"severity": "error", "file": "dts/edge_io_ring.dts", "msg": f"missing {needle}"})

    # Ensure DTS documents SDA/SCL pins
    if "P0.26" not in dts or "P0.27" not in dts:
        findings.append({"severity": "error", "file": "dts/edge_io_ring.dts", "msg": "SDA/SCL pin comments missing"})

    errors = [f for f in findings if f["severity"] == "error"]
    report = {
        "ok": not errors,
        "error_count": len(errors),
        "findings": findings,
        "token": "RING_STATIC_ANALYSIS_PASS" if not errors else "RING_STATIC_ANALYSIS_FAIL",
        "physical_boot_claimed": False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "STATIC_ANALYSIS_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report["token"])
    for f in errors:
        print("ERR", f["file"], f["msg"])
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
