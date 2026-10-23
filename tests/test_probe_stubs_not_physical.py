"""Stub probe zeros must not be emitted as physical measurements."""

from __future__ import annotations

from edge_io_node.latency_probe import measure_latency_ms
from edge_io_node.packet_loss_probe import measure_packet_loss_pct


def test_stub_zeros_are_unavailable_not_physical() -> None:
    latency = measure_latency_ms("example.invalid")
    loss = measure_packet_loss_pct("example.invalid")

    assert not isinstance(latency, (int, float))
    assert not isinstance(loss, (int, float))

    for result, value_key in ((latency, "latency_ms"), (loss, "packet_loss_pct")):
        assert result[value_key] == 0.0
        assert result["measurement_class"] == "unavailable"
        assert result["physical_measurement"] is False
        assert result["sensor_reading"] is False
        assert result["measurement_class"] != "physical"
