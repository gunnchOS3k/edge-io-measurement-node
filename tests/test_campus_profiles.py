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
