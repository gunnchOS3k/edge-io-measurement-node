import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from edge_io_node.telemetry_schema import FORBIDDEN_PII_FIELDS, TelemetrySample


def test_example_record_has_required_fields():
    sample = TelemetrySample.example()
    exported = sample.to_dict()
    for field in TelemetrySample.REQUIRED_EXPORT_FIELDS:
        assert field in exported


def test_opt_in_required():
    sample = TelemetrySample(
        timestamp_utc="2026-01-01T00:00:00Z",
        device_id_hash="hash_00001234",
        consent_flag=True,
        consent_state="opt_in_active",
        latency_ms=1.0,
        opt_in=True,
    )
    assert sample.to_dict()["latency_ms"] == 1.0


def test_no_raw_pii_fields_in_export():
    sample = TelemetrySample.example()
    exported = sample.to_dict()
    assert not FORBIDDEN_PII_FIELDS.intersection(exported.keys())


def test_legacy_mapping():
    legacy = {
        "timestamp_iso": "2026-02-01T12:00:00Z",
        "device_id_hash": "legacy_hash_001",
        "packet_loss_pct": 1.5,
        "cpu_pct": 12.0,
        "opt_in": True,
    }
    sample = TelemetrySample.from_legacy(legacy)
    exported = sample.to_dict()
    assert exported["packet_loss_pct"] == 1.5
    assert exported["cpu_pct"] == 12.0


def test_example_files_validate():
    root = Path(__file__).resolve().parents[1]
    json_path = root / "examples" / "sample_telemetry.json"
    if json_path.exists():
        import json

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        sample = TelemetrySample.from_legacy(payload)
        sample.validate()
        sample.to_dict()
