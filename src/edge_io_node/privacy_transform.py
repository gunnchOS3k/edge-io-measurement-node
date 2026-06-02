"""Sanitize measurement exports."""
from __future__ import annotations

FORBIDDEN_KEYS = {"user_id", "email", "phone", "precise_gps", "student_id", "device_serial"}


def sanitize(record: dict) -> dict:
    out = {k: v for k, v in record.items() if k not in FORBIDDEN_KEYS}
    out["sanitized"] = True
    out["evidence_status"] = "smoke_test_only"
    return out


def assert_no_prohibited(record: dict, prohibited: list[str]) -> None:
    for key in prohibited:
        norm = key.replace("_", "")
        for k in record:
            if norm in k.replace("_", "").lower():
                raise ValueError(f"Prohibited field present: {k}")
