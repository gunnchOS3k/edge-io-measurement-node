"""Export campus measurements to 7GC format."""
from __future__ import annotations

import json
from pathlib import Path

from .measurement_plan import build_plan
from .privacy_transform import sanitize
from .synthetic_device_emulator import emulate_sample


def run_measurement(site_id: str, mode: str = "local-safe") -> dict:
    plan = build_plan(site_id, mode=mode)
    packet = emulate_sample(f"campus_{site_id}")
    clean = sanitize(packet)
    return {"plan": plan, "measurement": clean, "evidence_status": "smoke_test_only"}


def export_to_7gc(site_id: str, out_dir: Path | None = None) -> Path:
    out_dir = out_dir or Path("results/campus_measurements")
    out_dir.mkdir(parents=True, exist_ok=True)
    data = run_measurement(site_id)
    path = out_dir / f"{site_id}_7gc_export.json"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path
