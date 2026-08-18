"""Digital RQ3 measurement path: consent, anti-replay, IMU non-claim, export."""
from __future__ import annotations

import pytest

from edge_io_node.anti_replay import AntiReplayWindow, ReplayRejected
from edge_io_node.consent.lifecycle import ConsentRecord
from edge_io_node.research_export import export_research_pack
from edge_io_node.ring_e2e.classifier import SpatialInputClassifier
from edge_io_node.synthetic_device_emulator import emulate_samples


def test_consent_blocks_without_opt_in():
    c = ConsentRecord()
    c.acknowledge_summary()
    with pytest.raises(PermissionError):
        c.require_opt_in(site_id="gary", run_id="r1", affirmative=False)
    c.require_opt_in(site_id="gary", run_id="r1", affirmative=True)
    assert c.status == "active"
    c.withdraw()
    assert c.status == "withdrawn"


def test_anti_replay_rejects_reuse():
    w = AntiReplayWindow()
    w.require(1)
    w.require(2)
    with pytest.raises(ReplayRejected):
        w.require(1)


def test_imu_classifier_is_not_absolute_pose():
    intent = SpatialInputClassifier().classify({"ax": 0.5, "ay": 0.0, "gz": 0.0, "cal_conf": 1.0})
    assert intent.pose_claim == "relative_cues_only_not_absolute_pose"
    assert intent.spatial_accuracy == "PHYSICAL_PENDING"


def test_research_export_stays_synthetic(tmp_path):
    samples = emulate_samples(3)
    pack = export_research_pack(samples, site_id="gary", out_dir=tmp_path)
    assert pack["evidence_level"] == "synthetic"
    assert pack["spatial_accuracy"] == "PHYSICAL_PENDING"
    assert pack["imu_pose_claim"] == "relative_cues_only_not_absolute_pose"
    assert any("absolute pose" in n.lower() or "Not validated" in n for n in pack["non_claims"])
    with pytest.raises(ValueError):
        export_research_pack(samples, site_id="gary", evidence_level="controlled_device_measurement")
