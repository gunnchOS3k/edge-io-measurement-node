"""Board/DT pinout assumptions must match schematic netlist map."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def test_pinout_json_matches_board_h():
    pinout = json.loads((ROOT / "dts" / "pinout.json").read_text())
    board_h = (ROOT / "boards" / "arm" / "edge_io_ring" / "board.h").read_text()
    mapping = {
        "I2C_SDA": "RING_PIN_I2C_SDA",
        "I2C_SCL": "RING_PIN_I2C_SCL",
        "IMU_INT": "RING_PIN_IMU_INT",
        "CHG_STATUS": "RING_PIN_CHG_STATUS",
    }
    for net, macro in mapping.items():
        pin = pinout["gpio"][net]["pin"]
        m = re.search(rf"#define\s+{macro}\s+(\d+)", board_h)
        assert m, macro
        assert int(m.group(1)) == pin


def test_dts_mentions_gpio_pins():
    dts = (ROOT / "dts" / "edge_io_ring.dts").read_text()
    assert "bmi270@68" in dts
    assert "drv2605l@5a" in dts
    assert "gpios = <&gpio0 11 0>" in dts
    assert "gpios = <&gpio0 2 0>" in dts


def test_physical_boot_pending_token():
    pinout = json.loads((ROOT / "dts" / "pinout.json").read_text())
    assert pinout["physical_boot"] == "RING_PHYSICAL_BOOT_PENDING"
