import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from edge_io_node.telemetry_schema import TelemetrySample

def test_opt_in_required():
    s = TelemetrySample(
        "hash_00001234",
        "2026-01-01T00:00:00Z",
        consent_state="opt_in_active",
        latency_ms=1.0,
        opt_in=True,
    )
    assert s.to_dict()["latency_ms"] == 1.0
