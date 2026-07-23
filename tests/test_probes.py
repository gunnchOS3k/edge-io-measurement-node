import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from edge_io_node.probes import (
    probe_device_status,
    probe_jitter,
    probe_latency,
    probe_packet_loss,
    probe_rssi,
)


def test_latency_probe_shape():
    result = probe_latency()
    assert "latency_ms" in result


def test_packet_loss_probe_shape():
    result = probe_packet_loss(attempts=2)
    assert "packet_loss_pct" in result


def test_jitter_probe_shape():
    result = probe_jitter(samples=2)
    assert "jitter_ms" in result


def test_rssi_probe_shape():
    result = probe_rssi()
    assert "rssi_dbm" in result
    assert "network_type" in result


def test_device_status_probe_shape():
    result = probe_device_status()
    assert "cpu_pct" in result
    assert "battery_pct" in result
