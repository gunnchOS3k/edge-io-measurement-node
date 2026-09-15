"""Privacy transforms for edge telemetry."""
from __future__ import annotations

from edge_io_node.privacy_transform import (
    DENIED_EXPORT_FIELDS,
    export_readiness_report,
    transform_for_research_export,
)

ALLOWED_EXPORT = {
    "device_id_hash",
    "timestamp_iso",
    "latency_ms",
    "jitter_ms",
    "packet_loss_percent",
    "cpu_percent",
    "memory_percent",
    "privacy_tier",
    "consent_state",
}


def sanitize(sample: dict) -> dict:
    return transform_for_research_export(sample)


def privacy_report(samples: list[dict]) -> str:
    rep = export_readiness_report(samples)
    lines = [
        "# Privacy Report",
        "",
        f"- Samples processed: {rep['samples_total']}",
        f"- Exportable: {rep['samples_exportable']}",
        f"- Blocked (consent): {rep['samples_blocked_consent']}",
        f"- Denied-field occurrences stripped: {rep['denied_field_occurrences_stripped']}",
        "- Consent enforced: yes",
        "- PHYSICAL_EVT_PASS: false",
        f"- Denied field denylist size: {len(DENIED_EXPORT_FIELDS)}",
    ]
    return "\n".join(lines) + "\n"
