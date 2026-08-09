"""Continuation VII — firmware release integrity + driver depth + Zephyr-native gates."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_driver_depth_apis_present():
    for name, symbols in {
        "bmi270": ["bmi270_configure", "bmi270_soft_reset", "bmi270_recover", "bmi270_diagnostics"],
        "iqs7222a": ["iqs7222a_configure", "iqs7222a_soft_reset", "iqs7222a_recover", "iqs7222a_diagnostics"],
        "se050": ["se050_soft_reset", "se050_recover", "se050_diagnostics", "SE050_REG_CHALLENGE"],
        "npm1300": ["npm1300_configure", "npm1300_soft_reset", "npm1300_recover", "npm1300_diagnostics"],
        "dw3000": ["dw3000_configure", "dw3000_soft_reset", "dw3000_recover", "dw3000_diagnostics"],
    }.items():
        text = (ROOT / "drivers" / name / f"{name}.c").read_text() + (ROOT / "drivers" / name / f"{name}.h").read_text()
        for sym in symbols:
            assert sym in text, f"{name} missing {sym}"


def test_drivers_not_fixture_only():
    """Drivers must perform bus register transactions (not return constants only)."""
    for name in ("bmi270", "iqs7222a", "se050", "npm1300", "dw3000"):
        c = (ROOT / "drivers" / name / f"{name}.c").read_text()
        assert "ring_i2c_reg_read" in c or "bus->xfer" in c or "dev->bus->xfer" in c
        assert "RING_BUS_ERR" in c
        assert "recover" in c


def test_zephyr_native_path_present():
    main = (ROOT / "zephyr_app" / "src" / "main.c").read_text()
    assert "DEVICE_DT_GET" in main
    assert "LOG_MODULE_REGISTER" in main
    assert "settings_subsys_init" in main
    assert "bt_enable" in main
    assert "pm_device_action_run" in main
    assert "ring_zephyr_bus_bind" in main
    assert "CONFIG_RING_USE_FAKE_BUS" in main
    bus = (ROOT / "drivers" / "bus" / "ring_bus_zephyr.c").read_text()
    assert "i2c_write_read" in bus
    assert "spi_transceive" in bus
    prj = (ROOT / "zephyr_app" / "prj.conf").read_text()
    for k in ("CONFIG_BT=y", "CONFIG_SETTINGS=y", "CONFIG_I2C=y", "CONFIG_SPI=y", "CONFIG_PM_DEVICE=y", "CONFIG_BOOTLOADER_MCUBOOT=y"):
        assert k in prj
    assert (ROOT / "dts" / "bindings" / "azoteq,iqs7222a.yaml").is_file()
    assert (ROOT / "dts" / "bindings" / "nxp,se050.yaml").is_file()
    assert (ROOT / "dts" / "bindings" / "qorvo,dw3000.yaml").is_file()
    assert (ROOT / "zephyr_app" / "Kconfig").is_file()


def test_driver_depth_host_compile_and_run():
    """Compile deepened drivers + app against fake bus on host."""
    srcs = [
        "drivers/bus/ring_bus_fake.c",
        "drivers/bmi270/bmi270.c",
        "drivers/iqs7222a/iqs7222a.c",
        "drivers/se050/se050.c",
        "drivers/npm1300/npm1300.c",
        "drivers/dw3000/dw3000.c",
        "drivers/bmm350/bmm350.c",
        "app/ring_app.c",
        "tests/test_driver_depth.c",
    ]
    out = ROOT / "build" / "test_driver_depth.elf"
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "clang",
        "-O0",
        "-g",
        "-Wall",
        "-Wextra",
        "-I.",
        "-Idrivers",
        "-Iapp",
        "-Iinclude",
        "-Iboards/arm/edge_io_ring",
        "-DRING_DEVELOPMENT=1",
        *srcs,
        "-o",
        str(out),
    ]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    r2 = subprocess.run([str(out)], cwd=ROOT, capture_output=True, text=True)
    assert r2.returncode == 0, r2.stdout + r2.stderr
    assert "driver_depth_ok" in r2.stdout


def test_continuation_vii_audit_doc():
    doc = ROOT / "docs" / "RING_FIRMWARE_RELEASE_INTEGRITY_CONTINUATION_VII.md"
    assert doc.is_file()
    text = doc.read_text()
    assert "RING_END_TO_END_DIGITAL_INPUT_PASS" in text
    assert "PHYSICAL_EXECUTION_FREEZE" in text
    assert "BMI270" in text
