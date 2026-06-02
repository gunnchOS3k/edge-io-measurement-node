"""Write campus measurement reports."""
from pathlib import Path
import json

from .campus_export import export_to_7gc, run_measurement
from .campus_profiles import list_campus_profiles


def write_campus_bundle(site_id: str, mode: str = "local-safe") -> None:
    out = Path("results/campus_measurements")
    out.mkdir(parents=True, exist_ok=True)
    m = run_measurement(site_id, mode=mode)
    (out / f"{site_id}_measurement_plan.md").write_text(
        f"# Measurement plan — {site_id}\n\n```json\n{json.dumps(m['plan'], indent=2)}\n```\n",
        encoding="utf-8",
    )
    (out / f"{site_id}_privacy_report.md").write_text(
        f"# Privacy report — {site_id}\n\nTier: {m['plan']['privacy_tier']}\n\nEvidence: smoke_test_only\n",
        encoding="utf-8",
    )
    (out / f"{site_id}_sanitized_measurements.json").write_text(
        json.dumps(m["measurement"], indent=2) + "\n", encoding="utf-8",
    )
    export_to_7gc(site_id, out)


def run_all_campus(mode: str = "local-safe") -> None:
    for sid in list_campus_profiles():
        write_campus_bundle(sid, mode=mode)
