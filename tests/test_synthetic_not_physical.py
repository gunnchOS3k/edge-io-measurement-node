"""Synthetic fixtures must not be emitted as physical measurements."""

from __future__ import annotations

import pytest

from edge_io_node.collectors.base import MeasurementSession, build_batch
from edge_io_node.consent.lifecycle import ConsentRecord


def _session() -> MeasurementSession:
    consent = ConsentRecord()
    consent.acknowledge_summary()
    consent.require_opt_in(site_id="gary", run_id="syn", affirmative=True)
    session = MeasurementSession(
        run_id="syn",
        site_id="gary",
        profile="sense",
        duration_s=1,
        consent=consent,
    )
    session.samples = [
        {
            "timestamp": "2026-01-01T00:00:00Z",
            "latency_ms": 12.0,
            "quality_flags": ["ok", "emulator"],
        }
    ]
    return session


def test_synthetic_fixture_is_not_emitted_as_physical() -> None:
    session = _session()
    with pytest.raises(ValueError, match="synthetic fixture"):
        build_batch(
            session,
            evidence_level="controlled_device_measurement",
            collector="physical_device",
            source="DeterministicEmulatorCollector",
            device={
                "device_class": "emulator",
                "os_family": "linux",
                "model_label": "deterministic_emulator",
                "network_interfaces": ["wifi"],
            },
        )

    labeled = build_batch(
        session,
        evidence_level="synthetic",
        collector="deterministic_emulator",
        source="DeterministicEmulatorCollector",
        device={
            "device_class": "emulator",
            "os_family": "linux",
            "model_label": "deterministic_emulator",
            "network_interfaces": ["wifi"],
        },
    )
    assert labeled.payload["evidence_level"] == "synthetic"
    assert labeled.payload["provenance"]["notes"] == "Synthetic fixture"
    assert "Physical-device capture" not in labeled.payload["provenance"]["notes"]
