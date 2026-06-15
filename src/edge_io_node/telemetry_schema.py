"""Privacy-preserving telemetry schema (no PII)."""
from __future__ import annotations

from dataclasses import dataclass, asdict, fields
from datetime import datetime, timezone
from typing import Optional


FORBIDDEN_PII_FIELDS = {
    "email",
    "phone",
    "imei",
    "mac_address",
    "ssid",
    "bssid",
    "ip_address",
    "full_name",
    "student_id",
    "gps_lat",
    "gps_lon",
    "latitude",
    "longitude",
}


@dataclass
class TelemetrySample:
    timestamp_utc: str
    device_id_hash: str
    location_label: str = "unspecified_waypoint"
    gps_precision_bucket: str = "none"
    network_type: str = "unknown"
    rssi_dbm: Optional[float] = None
    latency_ms: Optional[float] = None
    jitter_ms: Optional[float] = None
    packet_loss_pct: Optional[float] = None
    download_mbps: Optional[float] = None
    upload_mbps: Optional[float] = None
    cpu_pct: Optional[float] = None
    battery_pct: Optional[float] = None
    device_temp_c: Optional[float] = None
    offline_ai_latency_ms: Optional[float] = None
    consent_flag: bool = False
    notes_redacted: str = ""
    # Legacy aliases retained for backward compatibility
    timestamp_iso: Optional[str] = None
    consent_state: str = "consent_pending"
    packet_loss_percent: Optional[float] = None
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    battery_percent: Optional[float] = None
    local_inference_ms: Optional[float] = None
    privacy_tier: str = "synthetic_tier_a"
    retention_policy: str = "delete_after_export_toy"
    opt_in: bool = False

    REQUIRED_EXPORT_FIELDS = (
        "timestamp_utc",
        "device_id_hash",
        "location_label",
        "gps_precision_bucket",
        "network_type",
        "consent_flag",
    )

    def validate(self) -> None:
        if any(field in self.__dict__ for field in FORBIDDEN_PII_FIELDS):
            raise ValueError("forbidden PII field present")
        if not self.device_id_hash or len(self.device_id_hash) < 8:
            raise ValueError("device_id_hash must be pseudonymous hash")
        if self.consent_state not in ("consent_pending", "opt_in_active", "opt_out"):
            raise ValueError("invalid consent_state")
        if self.gps_precision_bucket not in ("none", "coarse", "medium", "fine"):
            raise ValueError("invalid gps_precision_bucket")

    def _normalized(self) -> dict:
        data = asdict(self)
        if not data.get("timestamp_utc") and data.get("timestamp_iso"):
            data["timestamp_utc"] = data["timestamp_iso"]
        if data.get("packet_loss_pct") is None and data.get("packet_loss_percent") is not None:
            data["packet_loss_pct"] = data["packet_loss_percent"]
        if data.get("cpu_pct") is None and data.get("cpu_percent") is not None:
            data["cpu_pct"] = data["cpu_percent"]
        if data.get("battery_pct") is None and data.get("battery_percent") is not None:
            data["battery_pct"] = data["battery_percent"]
        if data.get("offline_ai_latency_ms") is None and data.get("local_inference_ms") is not None:
            data["offline_ai_latency_ms"] = data["local_inference_ms"]
        if data.get("consent_flag") or data.get("opt_in") or data.get("consent_state") == "opt_in_active":
            data["consent_flag"] = True
        return data

    def to_dict(self) -> dict:
        self.validate()
        data = self._normalized()
        if not data.get("consent_flag"):
            raise ValueError("Telemetry export requires consent_flag/opt_in/consent_state=opt_in_active")
        export_keys = set(self.REQUIRED_EXPORT_FIELDS) | {
            "rssi_dbm",
            "latency_ms",
            "jitter_ms",
            "packet_loss_pct",
            "download_mbps",
            "upload_mbps",
            "cpu_pct",
            "battery_pct",
            "device_temp_c",
            "offline_ai_latency_ms",
            "notes_redacted",
            "privacy_tier",
            "retention_policy",
        }
        return {k: data[k] for k in export_keys if k in data}

    @classmethod
    def from_legacy(cls, raw: dict) -> "TelemetrySample":
        data = dict(raw)
        if "timestamp_utc" not in data and data.get("timestamp_iso"):
            data["timestamp_utc"] = data["timestamp_iso"]
        if "timestamp_utc" in data and "timestamp_iso" not in data:
            data["timestamp_iso"] = data["timestamp_utc"]
        if data.pop("packet_loss_pct", None) is not None and "packet_loss_percent" not in data:
            data.setdefault("packet_loss_percent", raw.get("packet_loss_pct"))
        if data.get("opt_in") or data.get("consent_flag"):
            data.setdefault("consent_state", "opt_in_active")
            data.setdefault("consent_flag", True)
        if "cpu_pct" in data:
            data.setdefault("cpu_percent", data.get("cpu_pct"))
        valid = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid})

    @classmethod
    def example(cls) -> "TelemetrySample":
        return cls(
            timestamp_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            device_id_hash="sha256_demo_device_001",
            location_label="gary_library_waypoint_a",
            gps_precision_bucket="coarse",
            network_type="wifi",
            rssi_dbm=-62.0,
            latency_ms=18.4,
            jitter_ms=2.1,
            packet_loss_pct=0.0,
            download_mbps=42.5,
            upload_mbps=8.2,
            cpu_pct=21.0,
            battery_pct=78.0,
            device_temp_c=32.5,
            offline_ai_latency_ms=95.0,
            consent_flag=True,
            consent_state="opt_in_active",
            opt_in=True,
            notes_redacted="synthetic_example_record",
        )
