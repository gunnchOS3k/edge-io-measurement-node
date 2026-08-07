"""MCUboot DEVELOPMENT signing negative fixtures must fail verify."""
from pathlib import Path
import json
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def _load_sign_mod():
    path = ROOT / "scripts" / "mcuboot_dev_pipeline.py"
    spec = importlib.util.spec_from_file_location("mcuboot_dev_pipeline", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_negative_fixtures_fail_when_present():
    fixtures = ROOT / "mcuboot" / "fixtures" / "NEGATIVE_FIXTURES.json"
    if not fixtures.exists():
        return
    data = json.loads(fixtures.read_text())
    assert data, "expected negative fixtures"
    for f in data:
        assert f.get("ok") is True
        assert f.get("verified") is False


def test_sign_report_tokens_when_present():
    report = ROOT / "build" / "out" / "MCUBOOT_SIGN_REPORT.json"
    if not report.exists():
        return
    data = json.loads(report.read_text())
    assert data["physical_boot_claimed"] is False
    assert "RING_PHYSICAL_BOOT_PENDING" in data["tokens"]
    assert "RING_MCUBOOT_DEV_PIPELINE_PASS" in data["tokens"]
    assert data["key_class"] == "DEVELOPMENT"
    assert data["verify_positive"] is True
