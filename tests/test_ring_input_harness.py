"""Tests for ring input measurement harness."""

from __future__ import annotations

from edge_io_node.ring_input_harness import (
    PHYSICAL_RING_CLAIMED,
    STATUSES,
    RingInputMeasurementRun,
    RingInputValidator,
)


def test_validator_all_cases_pass():
    report = RingInputValidator().run()
    assert report.ok, report.failed
    assert report.physical_ring_claimed is False
    assert report.evidence_class == "SOFTWARE_SIMULATED"
    assert report.statuses["AUTHENTICATED_INPUT_PROTOCOL_PASS"] is True
    assert report.statuses["RING_PHYSICAL_PROTOTYPE_PENDING"] is True


def test_measurement_run():
    result = RingInputMeasurementRun().execute()
    assert result["validation"]["ok"]
    assert result["physical_ring_claimed"] is False
    assert result["simulated_sample_count"] >= 1
    assert result["latency"]["evidence_class"] == "SOFTWARE_SIMULATED"


def test_status_constants():
    assert STATUSES["AUTHENTICATED_INPUT_PROTOCOL_PASS"] is True
    assert STATUSES["RING_PHYSICAL_PROTOTYPE_PENDING"] is True
    assert PHYSICAL_RING_CLAIMED is False
