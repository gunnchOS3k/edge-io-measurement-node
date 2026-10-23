"""Sanitize measurement exports. This helper does not mint physical evidence."""
from __future__ import annotations

FORBIDDEN_KEYS = {
    "user_id",
    "email",
    "phone",
    "precise_gps",
    "student_id",
    "device_serial",
    "imei",
    "imsi",
    "mac_address",
    "name",
}

_SYNTHETIC_TOKENS = ("synthetic", "emulator", "fixture", "simulated", "smoke", "toy")
_PHYSICAL_LEVELS = {
    "physical",
    "physical_measurement",
    "physical_sensor",
    "controlled_device_measurement",
}


def _forbidden(key: str) -> bool:
    norm = key.replace("_", "").lower()
    return any(item.replace("_", "") in norm for item in FORBIDDEN_KEYS)


def _strip(value):
    if isinstance(value, dict):
        return {k: _strip(v) for k, v in value.items() if not _forbidden(str(k))}
    if isinstance(value, list):
        return [_strip(item) for item in value]
    return value


def sanitize(record: dict) -> dict:
    evidence = str(record.get("evidence_level") or "").lower()
    synthetic = evidence == "" or any(token in evidence for token in _SYNTHETIC_TOKENS)
    physical_claim = bool(record.get("physical_measurement")) or evidence in _PHYSICAL_LEVELS
    if physical_claim and synthetic:
        raise ValueError("Cannot label synthetic fixture output as a physical measurement")
    out = _strip(record)
    out["sanitized"] = True
    out["evidence_status"] = "smoke_test_only"
    return out
