"""BLE stub digital tests — pairing + anti-replay; no radio / no physical boot."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def _load_native():
    path = ROOT / "native_sim" / "native_sim_boot.py"
    spec = importlib.util.spec_from_file_location("native_sim_boot", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_ble_pair_and_replay_reject():
    mod = _load_native()
    ble = mod.BleStub()
    assert ble.start_advertise() == "ADV_OK"
    assert ble.connect() == "CONN_OK"
    st, resp = ble.pair(bytes(range(16)))
    assert st == "PAIR_OK"
    assert len(resp) == 16
    st2, _ = ble.pair(bytes(range(16)))
    assert st2 == "ERR_REPLAY"
    assert ble.paired is True


def test_ble_requires_connect():
    mod = _load_native()
    ble = mod.BleStub()
    st, _ = ble.pair(b"\x00" * 16)
    assert st == "ERR_NOT_CONNECTED"


def test_native_sim_includes_ble_events():
    mod = _load_native()
    report = mod.boot_sim()
    assert "ble_pair" in report["events"]
    assert "ble_replay_rejected" in report["events"]
    assert report["physical_boot"] is False
    assert report["token"] == "RING_PHYSICAL_BOOT_PENDING"
