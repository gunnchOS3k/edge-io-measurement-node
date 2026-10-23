from edge_io_node.campus_export import run_measurement
from edge_io_node.campus_profiles import list_campus_profiles
from edge_io_node.privacy_transform import sanitize


def test_all_profiles():
    assert len(list_campus_profiles()) == 7


def test_gaza_no_pii():
    m = run_measurement("gaza", mode="local-safe")
    assert "user_id" not in m["measurement"]
    assert m["measurement"]["sanitized"] is True


def test_sanitize():
    s = sanitize({"latency_ms": 1, "user_id": "x"})
    assert "user_id" not in s


def test_sanitize_strips_nested_identifiers_and_refuses_synthetic_physical():
    import pytest

    clean = sanitize({
        "latency_ms": 1,
        "evidence_level": "synthetic",
        "meta": {"email": "person@example.test", "note": "ok"},
    })
    assert "email" not in clean["meta"]
    assert clean["meta"]["note"] == "ok"
    assert clean["evidence_status"] == "smoke_test_only"
    with pytest.raises(ValueError, match="physical measurement"):
        sanitize({
            "latency_ms": 1,
            "evidence_level": "synthetic",
            "physical_measurement": True,
        })
