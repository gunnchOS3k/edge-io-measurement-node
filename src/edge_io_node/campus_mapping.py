"""Campus mapping envelope over edge_measurement_batch.v1."""
from __future__ import annotations

import hashlib
import json
from typing import Any

SLUG_TO_SITE = {
    "gary": "gary",
    "ghana": "ghana",
    "guyana": "guyana",
    "geelong": "geelong",
    "germany": "germany",
    "gaza": "gaza",
    "graham-land": "graham_land",
    "graham_land": "graham_land",
}


def _sha(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build_campus_mapping(
    *,
    site_id: str,
    campus_slug: str,
    phase: str,
    campus_requirement_id: str,
    space_id: str,
    evidence_ref: str,
    batch: dict[str, Any] | None = None,
    producer_commit: str = "0" * 40,
) -> dict[str, Any]:
    if campus_slug not in SLUG_TO_SITE and site_id not in SLUG_TO_SITE.values():
        raise ValueError(f"unknown campus: {campus_slug}")
    commit = producer_commit if len(producer_commit) == 40 else "0" * 40
    return {
        "schema_name": "gunnchos.campus_measurement_mapping",
        "schema_version": "1.0.0",
        "run_id": f"campus-map-{site_id}",
        "site_id": site_id,
        "campus_slug": campus_slug,
        "phase": phase,
        "campus_requirement_id": campus_requirement_id,
        "space_id": space_id,
        "coarse_grid_cell": "Z0",
        "measurement_point_id": f"{site_id}-mp-01",
        "campus_model_version": "CAMPUS_V2_PLANNING",
        "infrastructure_version": "NETWORK_DESIGN_V1",
        "evidence_ref": evidence_ref,
        "batch_sha256": _sha(batch or {"synthetic": True, "site_id": site_id}),
        "contains_person_path": False,
        "exact_minor_location": False,
        "producer": {"repository": "edge-io-measurement-node", "commit": commit},
    }


def reject_person_path(payload: dict[str, Any]) -> None:
    if payload.get("contains_person_path") or payload.get("exact_minor_location"):
        raise ValueError("person path / exact minor location is forbidden")
    privacy = payload.get("privacy") or {}
    if privacy.get("contains_direct_identifiers"):
        raise ValueError("direct identifiers are forbidden")
