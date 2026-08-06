"""Validate authenticated ring input events against protocol expectations."""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _load_reference_module():
    """Prefer sibling hardware-industrial-design reference implementation."""
    # validator.py → ring_input_harness → edge_io_node → src → repo → repos
    repos_root = Path(__file__).resolve().parents[4]
    candidates = [
        repos_root / "gunnchos-hardware-industrial-design" / "ring_input" / "python",
        Path(
            "/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/"
            "gunnchos-hardware-industrial-design/ring_input/python"
        ),
    ]
    for root in candidates:
        if (root / "authenticated_ring_input" / "__init__.py").exists():
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))
            return importlib.import_module("authenticated_ring_input")
    raise ImportError(
        "authenticated_ring_input reference not found; expected "
        "gunnchos-hardware-industrial-design/ring_input/python"
    )


@dataclass
class ValidationReport:
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    evidence_class: str = "SOFTWARE_SIMULATED"
    physical_ring_claimed: bool = False
    statuses: dict[str, bool] = field(
        default_factory=lambda: {
            "AUTHENTICATED_INPUT_PROTOCOL_PASS": False,
            "RING_PHYSICAL_PROTOTYPE_PENDING": True,
        }
    )

    @property
    def ok(self) -> bool:
        return len(self.failed) == 0 and "valid_accept" in self.passed

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "passed": self.passed,
            "failed": self.failed,
            "evidence_class": self.evidence_class,
            "physical_ring_claimed": self.physical_ring_claimed,
            "statuses": self.statuses,
        }


class RingInputValidator:
    """Runs positive/negative protocol cases for measurement evidence."""

    CASES = (
        "valid_accept",
        "bad_signature",
        "unknown_device",
        "wrong_target",
        "replay",
        "stale",
        "revoked",
        "low_confidence_destructive",
        "calibration_mismatch",
        "offline_paired",
        "fallback_available",
    )

    def run(self) -> ValidationReport:
        ari = _load_reference_module()
        report = ValidationReport()
        base = 1_700_000_000_000
        checks: dict[str, bool] = {}

        def pair():
            sm = ari.PairingStateMachine(
                device_id="ring-sim-001",
                user_id="user-alice",
                host_id="host-dsxl-01",
                device_secret=b"device-secret-software-only",
                permission_scope=[
                    "pointer_move",
                    "click",
                    "key_press",
                    "scroll",
                    "heartbeat",
                    "destructive_confirm",
                ],
            )
            sm.start_challenge()
            assert sm.host_verify(sm.device_respond())
            sm.confirm()
            return sm

        def pipeline():
            sm = pair()
            cal_reg = ari.CalibrationRegistry()
            cal = cal_reg.create(
                surface_id="desk-surface-a",
                device_id=sm.device_id,
                user_id=sm.user_id,
                now_ms=base,
            )
            sender = ari.AuthenticatedSender(
                pairing=sm,
                target_device_id=sm.host_id,
                surface_id=cal["surface_id"],
                calibration_id=cal["calibration_id"],
            )
            sender.open_session(offline=True, now_ms=base)
            recv = ari.AuthenticatedReceiver(host_id=sm.host_id, known_devices={sm.device_id})
            recv.calibration = cal_reg
            recv.now_ms = base
            recv.register_session(sender.export_session_material())
            return sm, sender, recv

        sm, sender, recv = pipeline()
        checks["valid_accept"] = recv.receive(
            sender.emit("pointer_move", confidence=0.95, ts_ms=base)
        )[0]

        _, sender, recv = pipeline()
        ev = sender.emit("click", confidence=0.95, ts_ms=base)
        ev["mac"] = "0" * 64
        checks["bad_signature"] = recv.receive(ev)[1] == ari.RejectReason.BAD_SIGNATURE

        _, sender, recv = pipeline()
        ev = sender.emit("click", confidence=0.95, ts_ms=base)
        recv.known_devices.clear()
        checks["unknown_device"] = recv.receive(ev)[1] == ari.RejectReason.UNKNOWN_DEVICE

        _, sender, recv = pipeline()
        ev = sender.emit("click", confidence=0.95, ts_ms=base)
        ev["target_device_id"] = "other-host"
        checks["wrong_target"] = recv.receive(ev)[1] == ari.RejectReason.WRONG_TARGET

        _, sender, recv = pipeline()
        ev = sender.emit("click", confidence=0.95, ts_ms=base)
        recv.receive(ev)
        checks["replay"] = recv.receive(ev)[1] == ari.RejectReason.REPLAY

        _, sender, recv = pipeline()
        checks["stale"] = (
            recv.receive(sender.emit("click", confidence=0.95, ts_ms=base - 60_000))[1]
            == ari.RejectReason.STALE
        )

        sm, sender, recv = pipeline()
        recv.revocation.revoke_device(sm.device_id)
        checks["revoked"] = (
            recv.receive(sender.emit("click", confidence=0.95, ts_ms=base))[1]
            == ari.RejectReason.REVOKED
        )

        _, sender, recv = pipeline()
        checks["low_confidence_destructive"] = (
            recv.receive(sender.emit("destructive_confirm", confidence=0.4, ts_ms=base))[1]
            == ari.RejectReason.LOW_CONFIDENCE_DESTRUCTIVE
        )

        _, sender, recv = pipeline()
        sender.calibration_id = "cal-mismatch"
        checks["calibration_mismatch"] = (
            recv.receive(sender.emit("click", confidence=0.95, ts_ms=base))[1]
            == ari.RejectReason.CALIBRATION_MISMATCH
        )

        checks["offline_paired"] = pair().is_paired_offline()

        fb = ari.SafeFallback()
        fb.engage("auth_fail")
        checks["fallback_available"] = fb.status()["available"] and fb.status()["fallback_active"]

        for name in self.CASES:
            (report.passed if checks.get(name) else report.failed).append(name)

        report.statuses["AUTHENTICATED_INPUT_PROTOCOL_PASS"] = report.ok
        report.statuses["RING_PHYSICAL_PROTOTYPE_PENDING"] = True
        return report
