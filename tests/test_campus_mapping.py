from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from edge_io_node.calibration_evidence import quarantine_invalid, synthetic_from_objectives
from edge_io_node.campus_mapping import build_campus_mapping, reject_person_path
from edge_io_node.privacy import sanitize

ZONES = {
    "gary": ("GARY.FULL.HARDWARE_REPAIR_LAB", "hardware_repair_lab", "FULL"),
    "ghana": ("GHANA.FULL.MENTOR_WORKSPACE", "mentor_workspace", "FULL"),
    "guyana": ("GUYANA.FULL.CLIMATE_GIS_STUDIO", "climate_gis_studio", "FULL"),
    "geelong": ("GEELONG.FULL.DESIGN_BUILD_STUDIO", "design_build_studio", "FULL"),
    "germany": ("GERMANY.FULL.INDUSTRY40_TWIN_LAB", "industry40_twin_lab", "FULL"),
    "gaza": ("GAZA.RECOVERY.OFFLINE_LEARNING_STUDIO", "offline_learning_studio", "FULL_RECOVERY_EDUCATION_HUB"),
    "graham_land": ("GRAHAM.FULL.NTN_LAB", "ntn_lab", "NON_ANTARCTIC_POLAR_EDUCATION_HUB"),
}


def test_seven_campus_mapping_no_person_path():
    for site, (req, space, phase) in ZONES.items():
        slug = "graham-land" if site == "graham_land" else site
        mapping = build_campus_mapping(
            site_id=site,
            campus_slug=slug,
            phase=phase,
            campus_requirement_id=req,
            space_id=space,
            evidence_ref=f"opt-{site}",
        )
        assert mapping["contains_person_path"] is False
        assert mapping["exact_minor_location"] is False
        reject_person_path(mapping)


def test_privacy_sanitize_still_strips_unlisted():
    clean = sanitize(
        {
            "device_id_hash": "hash_0001",
            "timestamp_iso": "t",
            "consent_state": "opt_in_active",
            "latency_ms": 1.0,
            "secret_field": "x",
        }
    )
    assert "secret_field" not in clean


def test_reject_person_path():
    with pytest.raises(ValueError):
        reject_person_path({"contains_person_path": True})


def test_quarantine_and_synthetic_residual():
    measured = synthetic_from_objectives(
        {
            "coverage": 0.8,
            "capacity": 20.0,
            "latency": 20.0,
            "jitter": 2.0,
            "packet_loss": 0.5,
        }
    )
    assert measured["latency"] == 23.0
    rejected = quarantine_invalid({"contains_person_path": True, "evidence_ref": "bad"})
    assert rejected
