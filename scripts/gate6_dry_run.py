#!/usr/bin/env python3
"""Gate 6 dry-run for edge-io-measurement-node.

Validates synthetic fixtures and templates only. Never claims physical PASS.
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHYS = ROOT / "physical_evidence"
FIXTURE = PHYS / "fixtures" / "synthetic_session_dry_run.json"
REPORT = PHYS / "GATE6_DRY_RUN_REPORT.json"
QUARANTINE = PHYS / "quarantine"
SIBLING_MATRIX = (
    ROOT.parent / "gunnchos-7gc-ai-ran-field-kit" / "protocols" / "controlled_pilot_matrix.csv"
)

REQUIRED_TEMPLATES = [
    "SESSION_MANIFEST_TEMPLATE.json",
    "CONSENT_RECORD_TEMPLATE.json",
    "CALIBRATION_RECORD_TEMPLATE.json",
    "DEVICE_MANIFEST_TEMPLATE.json",
    "NETWORK_MANIFEST_TEMPLATE.json",
    "ENVIRONMENT_MANIFEST_TEMPLATE.json",
]

REQUIRED_FIXTURE_FIELDS = (
    "evidence_id",
    "evidence_label",
    "domain",
    "mode",
    "status",
    "repository",
    "artifacts",
    "notes",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a JSON object")
    return data


def check_templates() -> dict:
    missing = [name for name in REQUIRED_TEMPLATES if not (PHYS / name).is_file()]
    return {
        "ok": not missing,
        "required": REQUIRED_TEMPLATES,
        "missing": missing,
        "quarantine_stub": (QUARANTINE / ".gitkeep").is_file(),
    }


def check_fixture() -> dict:
    errors: list[str] = []
    if not FIXTURE.is_file():
        return {"ok": False, "errors": [f"missing fixture: {FIXTURE}"], "path": str(FIXTURE)}
    data = load_json(FIXTURE)
    for key in REQUIRED_FIXTURE_FIELDS:
        if key not in data:
            errors.append(f"missing field: {key}")
    if data.get("evidence_label") != "SYNTHETIC_EXPERIMENT":
        errors.append("evidence_label must be SYNTHETIC_EXPERIMENT")
    if data.get("mode") != "DRY_RUN" and data.get("status") != "DRY_RUN_SYNTHETIC":
        errors.append("fixture must be labeled DRY_RUN / DRY_RUN_SYNTHETIC")
    if "SYNTHETIC" not in str(data.get("notes", "")).upper() and data.get("mode") != "DRY_RUN":
        errors.append("notes must clearly mark synthetic/dry-run")
    return {"ok": not errors, "errors": errors, "path": str(FIXTURE), "evidence_id": data.get("evidence_id")}


def check_pilot_matrix() -> dict:
    """Preserve 54-cell design reference; do not invent physical sessions."""
    if not SIBLING_MATRIX.is_file():
        return {
            "ok": True,
            "present": False,
            "cell_count": None,
            "eligible_physical_sessions": 0,
            "ref": str(SIBLING_MATRIX),
            "note": "Sibling matrix not found in this workspace; design remains 54 cells by contract",
            "design_cells": 54,
        }
    with SIBLING_MATRIX.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    n = len(rows)
    return {
        "ok": n == 54,
        "present": True,
        "cell_count": n,
        "eligible_physical_sessions": 0,
        "ref": str(SIBLING_MATRIX),
        "design_cells": 54,
        "note": "54-cell matrix preserved; physical sessions remain pending",
    }


def main() -> int:
    PHYS.mkdir(parents=True, exist_ok=True)
    QUARANTINE.mkdir(parents=True, exist_ok=True)
    (QUARANTINE / ".gitkeep").touch(exist_ok=True)

    templates = check_templates()
    fixture = check_fixture()
    matrix = check_pilot_matrix()
    harness_ok = templates["ok"] and fixture["ok"] and matrix["ok"]

    report = {
        "gate": "6",
        "repository": "edge-io-measurement-node",
        "mode": "dry_run",
        "started": utc_now(),
        "templates": templates,
        "fixture": fixture,
        "pilot_matrix": matrix,
        "statuses": {
            "GATE6_HARNESS": "GATE6_HARNESS_PASS" if harness_ok else "GATE6_HARNESS_FAIL",
            "FIELD_PILOT": "FIELD_PILOT_PENDING",
            "PHYSICAL_EVIDENCE": "PHYSICAL_EVIDENCE_PENDING",
        },
        "claim": "GATE6_HARNESS_PASS only — no physical field completion claimed",
        "finished": utc_now(),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": harness_ok, "report": str(REPORT), "statuses": report["statuses"]}, indent=2))
    return 0 if harness_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
