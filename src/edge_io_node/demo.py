"""Synthetic telemetry demo (privacy-preserving, opt-in required)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .export_to_7gc import export_sample
from .privacy import privacy_report, sanitize
from .synthetic_device_emulator import emulate_samples
from .telemetry_schema import TelemetrySample


def run_toy(n: int = 5) -> dict:
    raw_samples = []
    sanitized = []
    exports = []
    for raw in emulate_samples(n):
        s = TelemetrySample.from_legacy(raw)
        raw_samples.append(s.to_dict())
        clean = sanitize(s.to_dict())
        sanitized.append(clean)
        exports.append(export_sample(clean, site_id="gary"))
    return {
        "n_samples": len(raw_samples),
        "samples": raw_samples,
        "sanitized": sanitized,
        "exports": exports,
        "consent_status": "opt_in_active",
        "anonymization": "hash_only_no_pii",
        "note": "synthetic opt-in telemetry",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--toy", action="store_true")
    args = parser.parse_args(argv)
    if not args.toy:
        parser.error("Use --toy")
    out = run_toy()
    print(json.dumps(out, indent=2))
    e2e = Path("results") / "e2e"
    e2e.mkdir(parents=True, exist_ok=True)
    (e2e / "synthetic_telemetry.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    (e2e / "sanitized_telemetry.json").write_text(json.dumps(out["sanitized"], indent=2) + "\n", encoding="utf-8")
    (e2e / "seven_gc_export.json").write_text(json.dumps({"exports": out["exports"]}, indent=2) + "\n", encoding="utf-8")
    (e2e / "privacy_report.md").write_text(privacy_report(out["sanitized"]), encoding="utf-8")
    print(f"Wrote {e2e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
