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
        "MCUBOOT_PIPELINE_REPORT.json",
        "SHA256SUMS",
        "MCUBOOT_SIGN_REPORT.json",
        "VERSION.txt",
    ]
    missing = [r for r in required if not (OUT / r).exists()]
    build_pass = not missing

    pipe_ok = False
    pipe_path = OUT / "MCUBOOT_PIPELINE_REPORT.json"
    if pipe_path.exists():
        pipe = json.loads(pipe_path.read_text(encoding="utf-8"))
        pipe_ok = (
            pipe.get("verify_slot0")
            and pipe.get("verify_update")
            and pipe.get("verify_revert")
            and pipe.get("verify_factory")
            and pipe.get("anti_replay_ok")
            and pipe.get("physical_boot_claimed") is False
        )

    west_pass = False
    west_soft = True
    west_path = OUT / "ZEPHYR_WEST_PROBE.json"
    west_blockers: list[str] = []
    if west_path.exists():
        west = json.loads(west_path.read_text(encoding="utf-8"))
        west_pass = bool(west.get("west_build_pass"))
        west_soft = not west_pass
        west_blockers = list(west.get("blockers") or [])

    tokens: list[str] = []
    if build_pass:
        tokens.append("RING_MCU_TARGET_FIRMWARE_BUILD_PASS")
    else:
        tokens.append("RING_MCU_TARGET_FIRMWARE_BUILD_FAIL")
    if pipe_ok:
        tokens.append("RING_MCUBOOT_DEV_PIPELINE_PASS")
    else:
        tokens.append("RING_MCUBOOT_DEV_PIPELINE_FAIL")
    if west_pass:
        tokens.append("RING_ZEPHYR_WEST_BUILD_PASS")
    else:
        tokens.append("RING_ZEPHYR_WEST_BUILD_SOFT_SKIP")
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
        "mcuboot": "DEVELOPMENT sign/update/revert/factory-test/anti-replay pipeline",
        "zephyr_west_build_pass": west_pass,
        "zephyr_west_soft_skip": west_soft,
        "zephyr_west_blockers": west_blockers,
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
            "MCUboot: DEVELOPMENT sign/update/revert/factory-test/anti-replay.",
            "",
            "## Not claimed",
            "- Physical ring flash / boot",
            "- Production MCUboot keys",
            "- `RING_ZEPHYR_WEST_BUILD_PASS` unless west build truly succeeded",
            "",
            "## Zephyr / west",
            "Isolated `.toolchain/west-venv` when present; full SDK soft-skip documented in",
            "`docs/ZEPHYR_WEST_BLOCKER.md`.",
            "",
            "## Build",
            "```bash",
            "cd gate1_digital_fabrication/ring_firmware",
            "make clean && make all",
            "```",
            "",
            "## Artifacts",
            "`build/out/ring_firmware_{debug,release_development}.{elf,bin,hex,map}`",
            "`build/out/mcuboot_pipeline/` · `SHA256SUMS`",
            "",
        ]
    )
    (DOCS / "FIRMWARE_STATUS.md").write_text(body, encoding="utf-8")
    (GATE_DOCS / "RING_FIRMWARE_STATUS.md").write_text(body, encoding="utf-8")
    (OUT / "STATUS.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(" ".join(tokens))
    return 0 if build_pass and pipe_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
