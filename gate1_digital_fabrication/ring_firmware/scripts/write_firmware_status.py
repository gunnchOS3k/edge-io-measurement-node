#!/usr/bin/env python3
"""Write firmware status tokens after successful digital build (no physical boot claim)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "out"
DOCS = ROOT / "docs"
GATE_DOCS = ROOT.parent / "docs"


def main() -> int:
    required = [
        "ring_firmware_debug.elf",
        "ring_firmware_debug.bin",
        "ring_firmware_debug.hex",
        "ring_firmware_debug.map",
        "ring_firmware_release_development.elf",
        "ring_firmware_release_development.bin",
        "ring_firmware_release_development.hex",
        "ring_firmware_release_development.map",
        "ring_firmware_mcuboot_signed_dev.bin",
        "SHA256SUMS",
        "MCUBOOT_SIGN_REPORT.json",
        "VERSION.txt",
    ]
    missing = [r for r in required if not (OUT / r).exists()]
    build_pass = not missing
    tokens = []
    if build_pass:
        tokens.append("RING_MCU_TARGET_FIRMWARE_BUILD_PASS")
    else:
        tokens.append("RING_MCU_TARGET_FIRMWARE_BUILD_FAIL")
    tokens.append("RING_PHYSICAL_BOOT_PENDING")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sha = (OUT / "SHA256SUMS").read_text() if (OUT / "SHA256SUMS").exists() else ""
    report = {
        "generated_at_utc": ts,
        "board": "edge_io_ring_evt0",
        "mcu": "nRF52840",
        "label": "development",
        "tokens": tokens,
        "physical_boot_claimed": False,
        "missing_artifacts": missing,
        "toolchain": "clang -target armv7em-none-eabi freestanding (Zephyr-shaped board/DT)",
        "mcuboot": "DEVELOPMENT HMAC signing + tampered negative fixtures",
        "sha256sums": sha.strip().splitlines(),
    }
    DOCS.mkdir(parents=True, exist_ok=True)
    GATE_DOCS.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            "# Ring Firmware Status",
            "",
            f"Generated: `{ts}`",
            "",
            "```text",
            *tokens,
            "```",
            "",
            "Label: **development firmware** (freestanding ARM + host/native_sim).",
            "MCUboot: DEVELOPMENT signing only.",
            "",
            "## Not claimed",
            "- Physical ring flash / boot",
            "- Production MCUboot keys",
            "",
            "## Build",
            "```bash",
            "cd gate1_digital_fabrication/ring_firmware",
            "make clean && make all",
            "```",
            "",
            "## Artifacts",
            "`build/out/ring_firmware_{debug,release_development}.{elf,bin,hex,map}`",
            "`build/out/ring_firmware_mcuboot_signed_dev.bin` · `SHA256SUMS`",
            "",
        ]
    )
    (DOCS / "FIRMWARE_STATUS.md").write_text(body, encoding="utf-8")
    (GATE_DOCS / "RING_FIRMWARE_STATUS.md").write_text(body, encoding="utf-8")
    (OUT / "STATUS.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(" ".join(tokens))
    return 0 if build_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
