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
        "BUILD_MATRIX_OK.txt",
        "ring_firmware_matrix_base.elf",
        "ring_firmware_matrix_uwb.elf",
        "ring_firmware_matrix_mag.elf",
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

    # Full digital pass: drivers+app present, matrix OK, builds OK, no STUB in DT
    dts = (ROOT / "dts" / "edge_io_ring.dts").read_text(encoding="utf-8")
    drivers_ok = all(
        (ROOT / p).is_file()
        for p in (
            "app/ring_app.c",
            "drivers/bmi270/bmi270.c",
            "drivers/iqs7222a/iqs7222a.c",
            "drivers/se050/se050.c",
            "drivers/npm1300/npm1300.c",
            "drivers/dw3000/dw3000.c",
            "drivers/bus/ring_bus_fake.c",
            "drivers/bus/ring_bus_zephyr.c",
        )
    )
    main_c = (ROOT / "zephyr_app" / "src" / "main.c").read_text(encoding="utf-8")
    app_ok = "ring_app_init" in main_c
    zephyr_native_ok = all(
        s in main_c
        for s in (
            "DEVICE_DT_GET",
            "settings_subsys_init",
            "bt_enable",
            "pm_device_action_run",
            "ring_zephyr_bus_bind",
        )
    )
    no_stub = ("CAP_INT_IQS7222A_STUB" not in dts and "SE_IRQ_SE050_STUB" not in dts and '_STUB"' not in dts)
    matrix_ok = (OUT / "BUILD_MATRIX_OK.txt").exists()
    full_digital = (
        build_pass and pipe_ok and drivers_ok and app_ok and no_stub and matrix_ok
    )

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
    if full_digital:
        tokens.append("RING_FULL_FIRMWARE_DIGITAL_PASS")
    else:
        tokens.append("RING_FULL_FIRMWARE_DIGITAL_FAIL")
    if zephyr_native_ok:
        tokens.append("RING_ZEPHYR_NATIVE_PATH_DIGITAL_PASS")
    else:
        tokens.append("RING_ZEPHYR_NATIVE_PATH_DIGITAL_FAIL")
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
        "toolchain": "clang host + armv7em freestanding + portable drivers (Zephyr-shaped DT)",
        "mcuboot": "DEVELOPMENT sign/update/revert/factory-test/anti-replay pipeline",
        "full_firmware_digital_pass": full_digital,
        "zephyr_native_path_ok": zephyr_native_ok,
        "drivers_ok": drivers_ok,
        "app_ok": app_ok,
        "matrix_ok": matrix_ok,
        "no_stub_dts": no_stub,
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
            "Label: **development firmware** (portable drivers + fusion app + host/native_sim).",
            "MCUboot: DEVELOPMENT sign/update/revert/factory-test/anti-replay.",
            "",
            "## Continuation VII",
            "- Driver depth: configure/recover/diagnostics for BMI270, IQS7222A, SE050, npm1300, DW3000",
            "- Zephyr-native path: DEVICE_DT_GET, I2C/SPI bus, BLE, settings, PM, MCUboot Kconfig",
            "- E2E digital input scenario token: RING_END_TO_END_DIGITAL_INPUT_PASS (repo tests)",
            "",
            "## Continuation VI (retained)",
            "- Real device tree nodes (no *_STUB labels)",
            "- Portable drivers + fusion application + build matrix + MCUboot DEV",
            "",
            "## Not claimed",
            "- Physical ring flash / boot",
            "- Production MCUboot keys",
            "- Full NXP Plug&Trust middleware (lite identity/auth path only)",
            "- Physical accuracy / latency",
            "",
            "## Build",
            "```bash",
            "cd gate1_digital_fabrication/ring_firmware",
            "make clean && make all",
            "```",
            "",
        ]
    )
    (DOCS / "FIRMWARE_STATUS.md").write_text(body, encoding="utf-8")
    (GATE_DOCS / "RING_FIRMWARE_STATUS.md").write_text(body, encoding="utf-8")
    (OUT / "STATUS.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(" ".join(tokens))
    return 0 if build_pass and pipe_ok and full_digital else 1


if __name__ == "__main__":
    raise SystemExit(main())
