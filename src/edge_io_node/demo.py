"""Toy demo for edge measurement node."""
import argparse
import json
from edge_io_node.synthetic_device_emulator import emulate_sample
from edge_io_node.exporters.seven_gc_export import export_sample
from edge_io_node.telemetry_schema import TelemetrySample


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--toy", action="store_true")
    args = parser.parse_args()
    raw = emulate_sample("hash_demo_device")
    sample = TelemetrySample(
        device_id_hash=raw["device_id_hash"],
        timestamp_iso="2026-01-01T12:00:00Z",
        latency_ms=raw.get("latency_ms"),
        opt_in=True,
    )
    out = export_sample(sample)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
