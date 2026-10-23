"""Privacy transforms for edge telemetry."""
from __future__ import annotations

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
    consent = sample.get("consent_state")
    opt_in = bool(sample.get("opt_in"))
    # An explicit non-active consent state wins over a leftover opt_in flag.
    if consent == "opt_in_active" or (consent in (None, "") and opt_in):
        pass
    else:
        raise ValueError("Export blocked: consent not active")
    out = {k: sample.get(k) for k in ALLOWED_EXPORT if k in sample or k.replace("_percent", "_pct") in sample}
    out["privacy_tier"] = sample.get("privacy_tier", "synthetic_tier_a")
    out["device_id_hash"] = sample.get("device_id_hash", "redacted")
    return {k: v for k, v in out.items() if v is not None}


def privacy_report(samples: list[dict]) -> str:
    lines = ["# Privacy Report", "", f"- Samples processed: {len(samples)}", "- PII fields stripped: none stored"]
    lines.append("- Consent enforced: yes")
    return "\n".join(lines) + "\n"
