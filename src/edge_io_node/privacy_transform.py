"""Privacy transforms for campus / research export preparation.

Digital-only helpers. Does not claim physical Ring EVT PASS.
"""
from __future__ import annotations

from typing import Any, Mapping

DENIED_EXPORT_FIELDS = frozenset(
    {
        "raw_mac",
        "email",
        "phone",
        "name",
        "student_id",
        "gps_exact",
        "ssid_raw",
        "ip_address",
        "secret_field",
        "pii",
    }
)


def strip_denied_fields(sample: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in sample.items() if k not in DENIED_EXPORT_FIELDS}


def normalize_consent(sample: Mapping[str, Any]) -> str:
    if sample.get("consent_state") == "opt_in_active" or sample.get("opt_in") is True:
        return "opt_in_active"
    if sample.get("consent_state") == "withdrawn":
        return "withdrawn"
    return "not_active"


def transform_for_research_export(sample: Mapping[str, Any]) -> dict[str, Any]:
    consent = normalize_consent(sample)
    if consent != "opt_in_active":
        raise ValueError(f"Export blocked: consent={consent}")
    cleaned = strip_denied_fields(sample)
    out = {
        "device_id_hash": cleaned.get("device_id_hash", "redacted"),
        "timestamp_iso": cleaned.get("timestamp_iso"),
        "latency_ms": cleaned.get("latency_ms"),
        "jitter_ms": cleaned.get("jitter_ms"),
        "packet_loss_percent": cleaned.get("packet_loss_percent", cleaned.get("packet_loss_pct")),
        "cpu_percent": cleaned.get("cpu_percent", cleaned.get("cpu_pct")),
        "memory_percent": cleaned.get("memory_percent", cleaned.get("memory_pct")),
        "privacy_tier": cleaned.get("privacy_tier", "synthetic_tier_a"),
        "consent_state": consent,
        "export_channel": "research_digital",
    }
    return {k: v for k, v in out.items() if v is not None}


def export_readiness_report(samples: list[Mapping[str, Any]]) -> dict[str, Any]:
    ok = 0
    blocked = 0
    denied_hits = 0
    for s in samples:
        for k in DENIED_EXPORT_FIELDS:
            if k in s:
                denied_hits += 1
        try:
            transform_for_research_export(s)
            ok += 1
        except ValueError:
            blocked += 1
    return {
        "schema": "gunnchos.edge_io.privacy_export_readiness.v1",
        "evidence_class": "DRAFT_DIGITAL_CANDIDATE",
        "samples_total": len(samples),
        "samples_exportable": ok,
        "samples_blocked_consent": blocked,
        "denied_field_occurrences_stripped": denied_hits,
        "PHYSICAL_EVT_PASS": False,
        "notes": "Digital privacy export prep only; physical Ring EVT remains PHYSICAL_VALIDATION_PENDING",
    }
