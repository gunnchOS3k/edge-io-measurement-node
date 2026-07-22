"""Gate 2 Edge-IO contract, consent, privacy, and collector tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from edge_io_node.collectors.base import (
    DeterministicEmulatorCollector,
    MeasurementSession,
    PhysicalDeviceCollector,
    delete_session,
)
from edge_io_node.consent.lifecycle import ConsentRecord
from edge_io_node.contracts.validate import validate_batch
from edge_io_node.exporters.seven_gc_export import export_batch_to_7gc

FK = Path(__file__).resolve().parents[3] / "gunnchos-7gc-ai-ran-field-kit"
SCHEMA_DIR = FK / "contracts"


@pytest.fixture
def active_consent() -> ConsentRecord:
    c = ConsentRecord()
    c.acknowledge_summary()
    c.require_opt_in(site_id="gary", run_id="test-run", affirmative=True)
    return c


def test_collection_requires_consent():
    c = ConsentRecord()
    session = MeasurementSession(
        run_id="r1", site_id="gary", profile="learn", duration_s=10, consent=c
    )
    collector = DeterministicEmulatorCollector()
    with pytest.raises(PermissionError):
        collector.start(session)


def test_withdrawal_blocks_further_collection(active_consent):
    session = MeasurementSession(
        run_id="r2", site_id="gary", profile="learn", duration_s=10, consent=active_consent
    )
    collector = DeterministicEmulatorCollector()
    collector.start(session)
    collector.sample()
    active_consent.withdraw()
    with pytest.raises(PermissionError):
        collector.sample()


def test_delete_removes_local_session(tmp_path, active_consent):
    session = MeasurementSession(
        run_id="r3", site_id="gary", profile="create", duration_s=10, consent=active_consent
    )
    collector = DeterministicEmulatorCollector()
    collector.start(session)
    batch = collector.stop()
    path = tmp_path / "session.json"
    batch.write(path)
    assert path.exists()
    delete_session(session, path)
    assert session.deleted
    assert not path.exists()
    assert session.samples == []


def test_prohibited_fields_rejected_recursively(active_consent):
    session = MeasurementSession(
        run_id="r4", site_id="gary", profile="sense", duration_s=10, consent=active_consent
    )
    collector = DeterministicEmulatorCollector()
    collector.start(session)
    batch = collector.stop()
    doc = batch.to_dict()
    doc["annotations"] = {"contact": {"email": "student@example.edu"}}
    with pytest.raises(Exception):
        validate_batch(doc, schema_dir=SCHEMA_DIR)


def test_invalid_ranges_fail(active_consent):
    session = MeasurementSession(
        run_id="r5", site_id="gary", profile="learn", duration_s=10, consent=active_consent
    )
    collector = DeterministicEmulatorCollector()
    collector.start(session)
    batch = collector.stop()
    doc = batch.to_dict()
    doc["measurements"][0]["latency_ms"] = -5
    with pytest.raises(Exception):
        validate_batch(doc, schema_dir=SCHEMA_DIR)


def test_unsupported_major_schema_fails(active_consent):
    session = MeasurementSession(
        run_id="r6", site_id="gary", profile="learn", duration_s=10, consent=active_consent
    )
    collector = DeterministicEmulatorCollector()
    collector.start(session)
    batch = collector.stop()
    doc = batch.to_dict()
    doc["schema_version"] = "2.0.0"
    with pytest.raises(Exception):
        validate_batch(doc, schema_dir=SCHEMA_DIR)


def test_missing_producer_commit_fails(active_consent):
    session = MeasurementSession(
        run_id="r7", site_id="gary", profile="learn", duration_s=10, consent=active_consent
    )
    collector = DeterministicEmulatorCollector()
    collector.start(session)
    batch = collector.stop()
    doc = batch.to_dict()
    doc["producer"]["commit"] = "abc"
    with pytest.raises(Exception):
        validate_batch(doc, schema_dir=SCHEMA_DIR)


def test_synthetic_and_measured_distinguishable(active_consent):
    session = MeasurementSession(
        run_id="r8", site_id="gary", profile="learn", duration_s=10, consent=active_consent
    )
    collector = DeterministicEmulatorCollector()
    collector.start(session)
    batch = collector.stop()
    assert batch.payload["evidence_level"] == "synthetic"
    assert batch.payload["provenance"]["collector"] == "deterministic_emulator"
    validate_batch(batch.payload, schema_dir=SCHEMA_DIR)


def test_export_validates_against_canonical_schema(tmp_path, active_consent):
    session = MeasurementSession(
        run_id="r9", site_id="gary", profile="learn", duration_s=10, consent=active_consent
    )
    collector = DeterministicEmulatorCollector()
    collector.start(session)
    for _ in range(3):
        collector.sample()
    batch = collector.stop()
    src = tmp_path / "session.json"
    out = tmp_path / "01_edge_measurements.json"
    batch.write(src)
    export_batch_to_7gc(src, out, schema_dir=SCHEMA_DIR)
    validate_batch(out, schema_dir=SCHEMA_DIR)


def test_physical_collector_does_not_emulate():
    c = ConsentRecord()
    c.acknowledge_summary()
    c.require_opt_in(site_id="gary", run_id="phys", affirmative=True)
    session = MeasurementSession(
        run_id="phys", site_id="gary", profile="learn", duration_s=10, consent=c
    )
    with pytest.raises(RuntimeError, match="No physical measurement backend"):
        PhysicalDeviceCollector().start(session)


def test_valid_fixture_from_field_kit():
    path = FK / "fixtures/valid/edge_measurement_batch.valid.json"
    if path.exists():
        validate_batch(path, schema_dir=SCHEMA_DIR)
