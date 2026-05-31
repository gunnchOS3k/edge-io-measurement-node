"""Synthetic telemetry demo (privacy-preserving, opt-in required)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .export_to_7gc import export_sample
from .synthetic_device_emulator import emulate_samples
from .telemetry_schema import TelemetrySample


def run_toy(n: int = 5) -> dict:
    samples = []
    for raw in emulate_samples(n):
        s = TelemetrySample(**raw)
        exported = export_sample(s.to_dict(), site_id="gary")
        samples.append(exported)
    return {"n_samples": len(samples), "samples": samples, "note": "synthetic opt-in telemetry"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--toy", action="store_true")
    args = parser.parse_args(argv)
    if not args.toy:
        parser.error("Use --toy")
    out = run_toy()
    print(json.dumps(out, indent=2))
    path = Path("results") / "edge_io_toy_export.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
