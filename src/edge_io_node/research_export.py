"""Research export with provenance. Never upgrades synthetic to physical."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .anti_replay import AntiReplayWindow, ReplayRejected, stamp_sample
from .privacy import sanitize
from .telemetry_schema import TelemetrySample


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_commit(repo_root: Path | None = None) -> str:
    root = repo_root or Path(__file__).resolve().parents[2]
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return "unknown"


def export_research_pack(
    samples: list[dict[str, Any]],
    *,
    site_id: str,
    evidence_level: str = "synthetic",
    out_dir: Path | None = None,
) -> dict[str, Any]:
    if evidence_level == "controlled_device_measurement":
        raise ValueError("research_export refuses to mint physical evidence from this helper")
    window = AntiReplayWindow()
    sanitized = []
    for i, raw in enumerate(samples, start=1):
        window.require(i)
        sample = TelemetrySample.from_legacy(raw)
        clean = sanitize(sample.to_dict())
        sanitized.append(stamp_sample(clean, i, nonce=hashlib.sha256(f"{site_id}:{i}".encode()).hexdigest()[:12]))
    pack = {
        "schema_name": "gunnchos.edge_research_export",
        "schema_version": "1.0.0",
        "site_id": site_id,
        "evidence_level": evidence_level,
        "spatial_accuracy": "PHYSICAL_PENDING",
        "imu_pose_claim": "relative_cues_only_not_absolute_pose",
        "n_samples": len(sanitized),
        "samples": sanitized,
        "provenance": {
            "repository": "edge-io-measurement-node",
            "commit": git_commit(),
            "generated_at": utc_now_iso(),
            "collector": "research_export",
        },
        "non_claims": [
            "Not a physical ring measurement",
            "Not validated absolute pose",
            "Not University of Oulu affiliation",
            "Absolute spatial accuracy remains PHYSICAL_PENDING",
        ],
    }
    dest = out_dir or Path("results/research_export")
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"{site_id}_research_export.json"
    path.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    pack["wrote"] = str(path)
    return pack


__all__ = ["export_research_pack", "ReplayRejected", "utc_now_iso"]
