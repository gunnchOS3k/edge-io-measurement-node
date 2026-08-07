"""Anti-replay + MCUboot DEV pipeline digital tests."""
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]


def _load_pipeline():
    path = ROOT / "scripts" / "mcuboot_dev_pipeline.py"
    spec = importlib.util.spec_from_file_location("mcuboot_dev_pipeline", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_anti_replay_monotonic():
    mod = _load_pipeline()
    seen: set[int] = set()
    assert mod.anti_replay_accept(seen, 1) is True
    assert mod.anti_replay_accept(seen, 2) is True
    assert mod.anti_replay_accept(seen, 2) is False
    assert mod.anti_replay_accept(seen, 1) is False
    assert mod.anti_replay_accept(seen, 3) is True


def test_pipeline_report_tokens_when_present():
    report = ROOT / "build" / "out" / "MCUBOOT_PIPELINE_REPORT.json"
    if not report.exists():
        # Allow collection before make mcuboot
        return
    data = json.loads(report.read_text())
    assert data["physical_boot_claimed"] is False
    assert "RING_MCUBOOT_DEV_PIPELINE_PASS" in data["tokens"]
    assert "RING_PHYSICAL_BOOT_PENDING" in data["tokens"]
    assert data["verify_slot0"] and data["verify_update"]
    assert data["verify_revert"] and data["verify_factory"]
    assert data["anti_replay_ok"] is True
    assert data["swap_state"]["active_slot"] == "slot0"
    assert data["swap_state"]["confirmed"] is True


def test_pipeline_fixture_files_when_present():
    base = ROOT / "mcuboot" / "fixtures" / "pipeline"
    if not (base / "PIPELINE_FIXTURES.json").exists():
        return
    for name in (
        "slot1_update_signed_dev.bin",
        "revert_signed_dev.bin",
        "factory_test_signed_dev.bin",
        "tampered_update.bin",
        "replay_slot0_counter.bin",
    ):
        assert (base / name).exists(), name
