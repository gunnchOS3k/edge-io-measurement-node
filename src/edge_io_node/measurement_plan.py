"""Build campus measurement plans."""
from __future__ import annotations

from .campus_profiles import load_campus_profile


def build_plan(site_id: str, mode: str = "local-safe") -> dict:
    p = load_campus_profile(site_id)
    return {
        "site_id": site_id,
        "mode": mode,
        "allowed": p["allowed_measurements"],
        "prohibited": p["prohibited_measurements"],
        "consent_mode": p["consent_mode"],
        "privacy_tier": p["privacy_tier"],
        "evidence_status": "smoke_test_only",
        "needs_local_validation": True,
    }
