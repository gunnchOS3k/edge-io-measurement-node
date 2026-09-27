"""Synthetic measurement residuals for campus calibration (not field evidence)."""
from __future__ import annotations

from typing import Any


def synthetic_from_objectives(objectives: dict[str, float]) -> dict[str, float]:
    return {
        "coverage": max(0.0, objectives["coverage"] - 0.04),
        "capacity": max(0.0, objectives["capacity"] - 1.5),
        "latency": objectives["latency"] + 3.0,
        "jitter": objectives["jitter"] + 0.4,
        "packet_loss": objectives["packet_loss"] + 0.2,
    }


def quarantine_invalid(evidence: dict[str, Any]) -> list[dict[str, str]]:
    rejected = []
    if evidence.get("contains_person_path"):
        rejected.append(
            {"evidence_ref": str(evidence.get("evidence_ref", "unknown")), "reason": "person path"}
        )
    if evidence.get("quarantined"):
        rejected.append(
            {"evidence_ref": str(evidence.get("evidence_ref", "unknown")), "reason": "quarantined"}
        )
    return rejected
