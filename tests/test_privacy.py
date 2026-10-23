import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from edge_io_node.privacy import sanitize


def test_sanitize_strips_unlisted():
    clean = sanitize({
        "device_id_hash": "hash_0001",
        "timestamp_iso": "t",
        "consent_state": "opt_in_active",
        "latency_ms": 1.0,
        "secret_field": "x",
    })
    assert "secret_field" not in clean


def test_opt_out_blocks_even_if_opt_in_flag_remains():
    import pytest

    with pytest.raises(ValueError, match="consent not active"):
        sanitize({
            "device_id_hash": "hash_0001",
            "consent_state": "opt_out",
            "opt_in": True,
            "latency_ms": 1.0,
        })
