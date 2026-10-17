import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from edge_io_node.privacy import privacy_report, sanitize
from edge_io_node.privacy_transform import export_readiness_report, transform_for_research_export


def test_sanitize_strips_unlisted():
    clean = sanitize(
        {
            "device_id_hash": "hash_0001",
            "timestamp_iso": "t",
            "consent_state": "opt_in_active",
            "latency_ms": 1.0,
            "secret_field": "x",
            "email": "a@b.c",
        }
    )
    assert "secret_field" not in clean
    assert "email" not in clean
    assert clean["consent_state"] == "opt_in_active"


def test_sanitize_blocks_without_consent():
    with pytest.raises(ValueError):
        sanitize({"device_id_hash": "h", "latency_ms": 1.0})


def test_export_readiness_report_digital_only():
    samples = [
        {
            "device_id_hash": "h1",
            "consent_state": "opt_in_active",
            "latency_ms": 2.0,
            "email": "nope@example.com",
        },
        {"device_id_hash": "h2", "latency_ms": 3.0},
    ]
    rep = export_readiness_report(samples)
    assert rep["samples_exportable"] == 1
    assert rep["samples_blocked_consent"] == 1
    assert rep["PHYSICAL_EVT_PASS"] is False
    assert "email" not in transform_for_research_export(samples[0])
    text = privacy_report(samples)
    assert "PHYSICAL_EVT_PASS: false" in text
