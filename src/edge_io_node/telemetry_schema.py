"""Privacy-preserving telemetry schema (no PII)."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class TelemetrySample:
    device_id_hash: str
    timestamp_iso: str
    latency_ms: Optional[float] = None
    jitter_ms: Optional[float] = None
    packet_loss_pct: Optional[float] = None
    rssi_dbm: Optional[float] = None
    cpu_pct: Optional[float] = None
    gpu_pct: Optional[float] = None
    opt_in: bool = False

    def to_dict(self) -> dict:
        if not self.opt_in:
            raise ValueError("Telemetry export requires opt_in=True")
        return asdict(self)
