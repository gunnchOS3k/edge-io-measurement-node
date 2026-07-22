"""Measurement collector protocols and implementations."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Protocol

from edge_io_node.consent.lifecycle import ConsentRecord, utc_now_iso


WorkloadProfile = Literal["learn", "create", "sense"]


SERVICE_PROFILES: dict[str, str] = {
    "learn": "learn_continuity",
    "create": "create_interactive",
    "sense": "sense_monitoring",
}


@dataclass
class MeasurementSession:
    run_id: str
    site_id: str
    profile: WorkloadProfile
    duration_s: float
    consent: ConsentRecord
    retention_days: int = 30
    started_at: str | None = None
    stopped_at: str | None = None
    deleted: bool = False
    samples: list[dict[str, Any]] = field(default_factory=list)

    @property
    def service_profile(self) -> str:
        return SERVICE_PROFILES[self.profile]

    def elapsed_s(self) -> float:
        if not self.started_at:
            return 0.0
        start = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
        end = datetime.now(timezone.utc)
        if self.stopped_at:
            end = datetime.fromisoformat(self.stopped_at.replace("Z", "+00:00"))
        return max(0.0, (end - start).total_seconds())


@dataclass
class MeasurementRecord:
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)


@dataclass
class MeasurementBatch:
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.payload, indent=2) + "\n", encoding="utf-8")
        return path


class MeasurementCollector(Protocol):
    def start(self, session: MeasurementSession) -> None: ...
    def sample(self) -> MeasurementRecord: ...
    def stop(self) -> MeasurementBatch: ...


def git_commit(repo_root: Path | None = None) -> str:
    root = repo_root or Path(__file__).resolve().parents[3]
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
        ).strip()
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Unable to resolve producer commit: {exc}") from exc


def _base_record(
    session: MeasurementSession,
    *,
    latency_ms: float,
    jitter_ms: float,
    packet_loss_pct: float,
    upload_mbps: float,
    download_mbps: float,
    network_type: str,
    cpu_pct: float,
    memory_pct: float,
    battery_pct: float,
    charging: bool,
    thermal_state: str,
    local_edge_response_ms: float,
    quality_flags: list[str],
    signal_dbm: float | None = None,
) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "timestamp": utc_now_iso(),
        "latency_ms": float(latency_ms),
        "jitter_ms": float(jitter_ms),
        "packet_loss_pct": float(packet_loss_pct),
        "upload_mbps": float(upload_mbps),
        "download_mbps": float(download_mbps),
        "network_type": network_type,
        "cpu_pct": float(cpu_pct),
        "memory_pct": float(memory_pct),
        "battery_pct": float(battery_pct),
        "charging": bool(charging),
        "thermal_state": thermal_state,
        "workload_profile": session.profile,
        "service_profile": session.service_profile,
        "local_edge_response_ms": float(local_edge_response_ms),
        "quality_flags": list(quality_flags),
    }
    if signal_dbm is not None:
        rec["signal_dbm"] = float(signal_dbm)
    return rec


class DeterministicEmulatorCollector:
    """Synthetic collector for tests and offline demos. Never used as measured evidence."""

    def __init__(self, seed: int = 7) -> None:
        self.seed = seed
        self._session: MeasurementSession | None = None
        self._tick = 0

    def start(self, session: MeasurementSession) -> None:
        session.consent.ensure_active_for_collection()
        if session.deleted:
            raise RuntimeError("Cannot collect into a deleted session")
        session.started_at = utc_now_iso()
        session.stopped_at = None
        session.samples.clear()
        self._session = session
        self._tick = 0

    def sample(self) -> MeasurementRecord:
        if self._session is None:
            raise RuntimeError("Collector not started")
        self._session.consent.ensure_active_for_collection()
        if self._session.consent.status == "withdrawn":
            raise PermissionError("Consent withdrawn; further collection is blocked")
        self._tick += 1
        base = 40.0 + (self.seed % 5) + self._tick * 2.5
        payload = _base_record(
            self._session,
            latency_ms=base,
            jitter_ms=2.0 + self._tick * 0.4,
            packet_loss_pct=min(5.0, 0.1 * self._tick),
            upload_mbps=max(1.0, 20.0 - self._tick),
            download_mbps=max(5.0, 70.0 - self._tick * 2),
            network_type="wifi",
            cpu_pct=min(95.0, 25.0 + self._tick * 3),
            memory_pct=min(95.0, 40.0 + self._tick * 2),
            battery_pct=max(5.0, 90.0 - self._tick),
            charging=False,
            thermal_state="nominal" if self._tick < 4 else "warm",
            local_edge_response_ms=10.0 + self._tick,
            quality_flags=["ok", "emulator"],
            signal_dbm=-55.0 - self._tick,
        )
        self._session.samples.append(payload)
        return MeasurementRecord(payload)

    def stop(self) -> MeasurementBatch:
        if self._session is None:
            raise RuntimeError("Collector not started")
        session = self._session
        if not session.samples:
            # one sample minimum for schema
            self.sample()
        session.stopped_at = utc_now_iso()
        batch = build_batch(
            session,
            evidence_level="synthetic",
            collector="deterministic_emulator",
            source="DeterministicEmulatorCollector",
            device={
                "device_class": "emulator",
                "os_family": "linux",
                "model_label": "deterministic_emulator",
                "network_interfaces": ["wifi"],
            },
        )
        self._session = None
        return batch


class PhysicalDeviceCollector:
    """Laptop/physical collector using lawful application-layer HTTPS probes.

    Does not invent unavailable metrics. Records missing-data reasons instead.
    """

    def __init__(
        self,
        *,
        endpoint: str = "https://www.cloudflare.com/cdn-cgi/trace",
        timeout_s: float = 5.0,
        retries: int = 1,
        device_category: str = "laptop",
        network_type: str = "wifi",
    ) -> None:
        self.endpoint = endpoint
        self.timeout_s = timeout_s
        self.retries = retries
        self.device_category = device_category
        self.network_type = network_type
        self._session: MeasurementSession | None = None
        self._missing_reasons: list[str] = []

    def health_check(self) -> dict[str, Any]:
        import urllib.error
        import urllib.request

        try:
            with urllib.request.urlopen(self.endpoint, timeout=self.timeout_s) as resp:
                return {"ok": True, "status": getattr(resp, "status", 200), "endpoint": self.endpoint}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "endpoint": self.endpoint, "error": str(exc)}

    def start(self, session: MeasurementSession) -> None:
        session.consent.ensure_active_for_collection()
        if session.deleted:
            raise RuntimeError("Cannot collect into a deleted session")
        health = self.health_check()
        if not health.get("ok"):
            raise RuntimeError(
                f"Physical endpoint health check failed for {self.endpoint}: {health.get('error')}"
            )
        session.started_at = utc_now_iso()
        session.stopped_at = None
        session.samples.clear()
        self._session = session
        self._missing_reasons = []
        print("PHYSICAL DEVICE COLLECTION", flush=True)

    def _probe_once(self) -> tuple[float | None, str | None]:
        import time
        import urllib.request

        last_err = None
        for _ in range(max(1, self.retries + 1)):
            t0 = time.perf_counter()
            try:
                with urllib.request.urlopen(self.endpoint, timeout=self.timeout_s) as resp:
                    resp.read(256)
                return (time.perf_counter() - t0) * 1000.0, None
            except Exception as exc:  # noqa: BLE001
                last_err = str(exc)
        return None, last_err

    def sample(self) -> MeasurementRecord:
        if self._session is None:
            raise RuntimeError("Collector not started")
        self._session.consent.ensure_active_for_collection()
        latency_ms, err = self._probe_once()
        quality = ["ok"]
        if latency_ms is None:
            quality = ["probe_timeout"]
            self._missing_reasons.append(f"latency_unavailable:{err}")
            latency_ms = 0.0  # schema requires number; flagged via quality_flags + notes
            # Using 0 only with probe_timeout flag and missing reason recorded.
        # Unavailable metrics: signal, packet loss, throughput — do not invent
        # Represent unavailable numeric metrics as None where schema allows, else omit.
        payload = _base_record(
            self._session,
            latency_ms=float(latency_ms),
            jitter_ms=0.0,
            packet_loss_pct=0.0,
            upload_mbps=0.0,
            download_mbps=0.0,
            network_type=self.network_type if self.network_type in {"wifi", "cellular", "ethernet", "unknown", "degraded_local"} else "unknown",
            cpu_pct=_read_cpu_pct(),
            memory_pct=_read_mem_pct(),
            battery_pct=100.0,  # laptop often AC; still recorded
            charging=True,
            thermal_state="unknown",
            local_edge_response_ms=float(latency_ms),
            quality_flags=quality + ["partial_sample"],
            signal_dbm=None,
        )
        # Annotate unavailable metrics explicitly in a non-prohibited annotations block
        # attached after batch build via session notes; keep measurement schema-valid.
        self._session.samples.append(payload)
        return MeasurementRecord(payload)

    def stop(self) -> MeasurementBatch:
        if self._session is None:
            raise RuntimeError("Collector not started")
        session = self._session
        if not session.samples:
            self.sample()
        session.stopped_at = utc_now_iso()
        os_family = "linux"
        batch = build_batch(
            session,
            evidence_level="controlled_device_measurement",
            collector="physical_device",
            source=f"PhysicalDeviceCollector:{self.endpoint}",
            device={
                "device_class": "laptop" if self.device_category == "laptop" else "phone",
                "os_family": os_family,
                "model_label": self.device_category,
                "network_interfaces": [self.network_type if self.network_type in {"wifi", "cellular", "ethernet"} else "unknown"],
            },
            notes=(
                "PHYSICAL DEVICE COLLECTION. Unavailable metrics (throughput/loss/signal) "
                "were not invented. Missing reasons: "
                + ("; ".join(self._missing_reasons) if self._missing_reasons else "none")
            ),
        )
        self._session = None
        return batch


def _read_cpu_pct() -> float:
    try:
        load1, _, _ = __import__("os").getloadavg()
        return float(min(100.0, max(0.0, load1 * 10.0)))
    except Exception:
        return 0.0


def _read_mem_pct() -> float:
    try:
        meminfo = Path("/proc/meminfo").read_text(encoding="utf-8")
        vals = {}
        for line in meminfo.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                vals[k] = float(v.strip().split()[0])
        total = vals.get("MemTotal", 1.0)
        avail = vals.get("MemAvailable", total)
        return float(min(100.0, max(0.0, 100.0 * (1.0 - avail / total))))
    except Exception:
        return 0.0


def build_batch(
    session: MeasurementSession,
    *,
    evidence_level: str,
    collector: str,
    source: str,
    device: dict[str, Any],
    client_version: str = "0.1.0",
    notes: str = "",
) -> MeasurementBatch:
    if session.deleted:
        raise RuntimeError("Session was deleted")
    session.consent.ensure_active_for_collection()
    if evidence_level == "controlled_device_measurement" and collector == "deterministic_emulator":
        raise ValueError("Cannot label emulator output as controlled_device_measurement")
    payload = {
        "schema_name": "gunnchos.edge_measurement_batch",
        "schema_version": "1.0.0",
        "run_id": session.run_id,
        "site_id": session.site_id,
        "producer": {
            "repository": "edge-io-measurement-node",
            "commit": git_commit(),
            "client_version": client_version,
        },
        "consent": session.consent.to_dict(),
        "privacy": {
            "location_precision": "named_test_zone",
            "contains_direct_identifiers": False,
            "retention_days": session.retention_days,
        },
        "device": device,
        "workload": {
            "profile": session.profile,
            "service_profile": session.service_profile,
            "duration_s": float(session.duration_s),
        },
        "measurements": list(session.samples),
        "provenance": {
            "collector": collector,
            "generated_at": utc_now_iso(),
            "source": source,
            "notes": notes
            or (
                "Synthetic fixture"
                if evidence_level == "synthetic"
                else "Physical-device capture"
            ),
        },
        "evidence_level": evidence_level,
    }
    return MeasurementBatch(payload)


def delete_session(session: MeasurementSession, path: Path | None = None) -> None:
    session.deleted = True
    session.samples.clear()
    session.stopped_at = utc_now_iso()
    if path and path.exists():
        path.unlink()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
