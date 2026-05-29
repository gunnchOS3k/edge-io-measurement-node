"""Export telemetry to 7GC-compatible format."""
from edge_io_node.telemetry_schema import TelemetrySample


def export_sample(sample: TelemetrySample, site_id: str = "gary") -> dict:
    return {
        "site_id": site_id,
        "telemetry": sample.to_dict(),
        "schema": "edge-io-telemetry-v1",
    }
