"""Privacy-preserving telemetry schema (no PII)."""
from __future__ import annotations

from dataclasses import dataclass, asdict, fields
from typing import Optional


@dataclass
class TelemetrySample:
    device_id_hash: str
    timestamp_iso: str
    consent_state: str = "consent_pending"
    latency_ms: Optional[float] = None
    jitter_ms: Optional[float] = None
    packet_loss_percent: Optional[float] = None
    rssi_dbm: Optional[float] = None
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    battery_percent: Optional[float] = None
    local_inference_ms: Optional[float] = None
    privacy_tier: str = "synthetic_tier_a"
    retention_policy: str = "delete_after_export_toy"
    opt_in: bool = False

    def validate(self) -> None:
        if not self.device_id_hash or len(self.device_id_hash) < 8:
            raise ValueError("device_id_hash must be pseudonymous hash")
        if self.consent_state not in ("consent_pending", "opt_in_active", "opt_out"):
            raise ValueError("invalid consent_state")

    def to_dict(self) -> dict:
        self.validate()
        if self.consent_state != "opt_in_active" and not self.opt_in:
            raise ValueError("Telemetry export requires opt_in or opt_in_active consent")
        return asdict(self)

    @classmethod
    def from_legacy(cls, raw: dict) -> "TelemetrySample":
        """Map older opt_in-only payloads."""
        data = dict(raw)
        if data.pop("packet_loss_pct", None) is not None:
            data.setdefault("packet_loss_percent", raw.get("packet_loss_pct"))
        if data.get("opt_in"):
            data.setdefault("consent_state", "opt_in_active")
        if "cpu_pct" in data:
            data.setdefault("cpu_percent", data.pop("cpu_pct"))
        valid = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid})
