"""Continuation VI — full firmware digital pass gates."""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_no_stub_labels_in_dts():
    dts = (ROOT / "dts" / "edge_io_ring.dts").read_text()
    assert "CAP_INT_IQS7222A_STUB" not in dts
    assert "SE_IRQ_SE050_STUB" not in dts
    assert '_STUB"' not in dts
    assert "bmi270@68" in dts
    assert "iqs7222a@44" in dts
    assert "se050@48" in dts
    assert "npm1300@6b" in dts
    assert "dwm3001c@0" in dts
    assert "P0.20" in dts or "gpio0 20" in dts


def test_pinout_final_not_stub():
    pinout = json.loads((ROOT / "dts" / "pinout.json").read_text())
    assert pinout["gpio"]["CAP_INT"]["status"] == "FINAL"
    assert pinout["gpio"]["SE_IRQ"]["status"] == "FINAL"
    assert pinout["gpio"]["NPM_INT"]["status"] == "FINAL"
    assert pinout["gpio"]["UWB_CS"]["pin"] == 20
    assert pinout["physical_boot"] == "RING_PHYSICAL_BOOT_PENDING"
    assert "STUB" not in pinout["i2c_devices"]["IQS7222A"]["status"]


def test_board_h_has_new_pins():
    board_h = (ROOT / "boards" / "arm" / "edge_io_ring" / "board.h").read_text()
    for macro in (
        "RING_PIN_CAP_INT",
        "RING_PIN_SE_IRQ",
        "RING_PIN_NPM_INT",
        "RING_PIN_UWB_CS",
        "RING_I2C_ADDR_IQS7222A",
        "RING_I2C_ADDR_SE050",
        "RING_I2C_ADDR_NPM1300",
    ):
        assert re.search(rf"#define\s+{macro}\s+", board_h)


def test_drivers_present():
    for rel in (
        "drivers/bmi270/bmi270.c",
        "drivers/iqs7222a/iqs7222a.c",
        "drivers/se050/se050.c",
        "drivers/npm1300/npm1300.c",
        "drivers/dw3000/dw3000.c",
        "app/ring_app.c",
        "drivers/bus/ring_bus_fake.c",
    ):
        assert (ROOT / rel).is_file(), rel


def test_zephyr_app_not_printk_only():
    main = (ROOT / "zephyr_app" / "src" / "main.c").read_text()
    assert "ring_app_init" in main
    assert "ring_app_tick" in main
    assert "printk loop" not in main.lower() or "fusion" in main


def test_host_sim_scenarios():
    py = sys.executable
    r = subprocess.run([py, str(ROOT / "host_sim" / "ring_host_sim.py"), "--self-check"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout
    assert "host_sim_ok" in r.stdout
