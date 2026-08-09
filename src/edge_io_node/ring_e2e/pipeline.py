"""RING_END_TO_END_DIGITAL_INPUT_PASS scenario runner."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .app_feedback import AppGameFeedback
from .ble_sim import BleTransportSim
from .classifier import SpatialInputClassifier
from .siblings import (
    firmware_host_sim,
    load_authenticated_ring_input,
    load_gunnchos_ring_adapter,
)
from .tokens import E2E_TOKEN, PHYSICAL_TOKEN


BASE_TS = 1_700_000_000_000

ACCEPT_EXERCISE = [
    "keyboard",
    "pointer",
    "scroll",
    "click",
    "chord",
    "game_button",
    "analog",
    "destructive",
]


@dataclass
class E2EReport:
    ok: bool
    token: str
    physical_token: str
    stages: dict[str, bool] = field(default_factory=dict)
    exercised: dict[str, bool] = field(default_factory=dict)
    actions: list[dict[str, Any]] = field(default_factory=list)
    rejects: list[dict[str, Any]] = field(default_factory=list)
    feedback: list[dict[str, Any]] = field(default_factory=list)
    evidence_class: str = "SOFTWARE_SIMULATED"
    physical_boot: bool = False
    errors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "token": self.token if self.ok else f"{E2E_TOKEN}_FAIL",
            "tokens": [
                self.token if self.ok else f"{E2E_TOKEN}_FAIL",
                self.physical_token,
            ],
            "stages": self.stages,
            "exercised": self.exercised,
            "actions": self.actions,
            "rejects": self.rejects,
            "feedback_count": len(self.feedback),
            "evidence_class": self.evidence_class,
            "physical_boot": self.physical_boot,
            "errors": self.errors,
        }


class RingEndToEndDigital:
    """Full digital ring → OS → app/game pipeline."""

    def __init__(self) -> None:
        self.ari = load_authenticated_ring_input()
        self.ring_os = load_gunnchos_ring_adapter()
        self.host_sim = firmware_host_sim()
        self.classifier = SpatialInputClassifier()
        self.ble = BleTransportSim()
        self.sink = AppGameFeedback()

    def _pair_and_calibrate(self, now_ms: int):
        sm = self.ari.PairingStateMachine(
            device_id="ring-e2e-001",
            user_id="user-e2e",
            host_id="host-dsxl-01",
            device_secret=b"e2e-device-secret-software-only",
            permission_scope=[
                "pointer_move",
                "click",
                "key_press",
                "key_release",
                "scroll",
                "heartbeat",
                "destructive_confirm",
            ],
        )
        sm.start_challenge()
        assert sm.host_verify(sm.device_respond())
        sm.confirm()
        cal_reg = self.ari.CalibrationRegistry()
        cal = cal_reg.create(
            surface_id="desk-surface-e2e",
            device_id=sm.device_id,
            user_id=sm.user_id,
            now_ms=now_ms,
        )
        sender = self.ari.AuthenticatedSender(
            pairing=sm,
            target_device_id=sm.host_id,
            surface_id=cal["surface_id"],
            calibration_id=cal["calibration_id"],
        )
        sender.open_session(offline=True, now_ms=now_ms)
        adapter = self.ring_os.RingInputAdapter(host_id=sm.host_id)
        adapter.attach_session(sender.export_session_material(), cal_reg)
        return sm, sender, adapter, cal_reg

    def run(self) -> E2EReport:
        report = E2EReport(
            ok=False,
            token=E2E_TOKEN,
            physical_token=PHYSICAL_TOKEN,
        )
        now = BASE_TS

        # Stage: fake buses → firmware fusion (host portable app logic)
        fw = self.host_sim.simulate("healthy", events=4, uwb=True)
        report.stages["fake_buses_firmware"] = bool(fw.get("init_ok")) and fw.get("result") == "HOST_SIM_PASS"
        if not report.stages["fake_buses_firmware"]:
            report.errors.append("firmware host_sim failed")
            return report

        fusion_frame = {
            "ax": 0.5,
            "ay": -0.2,
            "gz": 0.0,
            "cap_touch": True,
            "cal_conf": float(fw.get("calibration") or 1.0),
            "batt_pct": 80,
            "seq": 1,
            "mac_sha256": (fw["events"][0].get("mac_sha256") if fw.get("events") else ""),
        }
        report.stages["auth_packet_seed"] = bool(fusion_frame["mac_sha256"])

        sm, sender, adapter, cal_reg = self._pair_and_calibrate(now)
        report.stages["calibration"] = bool(cal_reg)
        report.stages["gunnchos_ring_service"] = adapter is not None

        # BLE connect
        self.ble.connect()
        report.stages["ble_sim"] = self.ble.connected

        # Exercise primary modalities (all should accept)
        for gesture in ACCEPT_EXERCISE:
            intent = self.classifier.classify(fusion_frame, gesture=gesture)
            report.stages["classifier"] = True
            ev = sender.emit(
                intent.event_type,
                confidence=intent.confidence,
                payload=intent.payload,
                ts_ms=now,
            )
            now += 20
            if not self.ble.send(ev):
                report.errors.append(f"ble_drop:{gesture}")
                report.exercised[gesture] = False
                continue
            pkt = self.ble.recv()
            assert pkt is not None
            action = adapter.ingest(pkt, now_ms=now)
            now += 5
            if action is None:
                report.rejects.append(
                    {
                        "gesture": gesture,
                        "reason": adapter.fallback.reason,
                        "confidence": intent.confidence,
                    }
                )
                self.sink.reject(adapter.fallback.reason or "reject", pkt)
                report.exercised[gesture] = False
                # Keep sender/receiver seq aligned after unexpected reject
                adapter.receiver.expected_seq[sender.session_id] = sender.next_seq
            else:
                routed = self.sink.route(
                    {
                        "kind": action.kind,
                        "event_type": action.event_type,
                        "confidence": action.confidence,
                        "payload": action.payload,
                    },
                    target="game" if gesture in ("game_button", "analog") else "app",
                )
                report.actions.append(routed)
                report.exercised[gesture] = True

        report.stages["input_routing"] = len(report.actions) > 0
        report.stages["app_game_feedback"] = len(self.sink.feedback) > 0
        report.feedback = list(self.sink.feedback)

        # Low-confidence destructive must reject (then realign seq)
        low = self.classifier.classify(fusion_frame, gesture="low_confidence_destructive")
        low_ev = sender.emit(
            low.event_type,
            confidence=low.confidence,
            payload=low.payload,
            ts_ms=now,
        )
        now += 20
        self.ble.send(low_ev)
        low_pkt = self.ble.recv()
        low_action = adapter.ingest(low_pkt, now_ms=now)
        report.exercised["low_confidence_destructive"] = low_action is None
        if low_action is None:
            report.rejects.append(
                {
                    "gesture": "low_confidence_destructive",
                    "reason": adapter.fallback.reason,
                    "confidence": low.confidence,
                }
            )
            self.sink.reject(adapter.fallback.reason or "low_confidence_destructive", low_pkt)
        adapter.receiver.expected_seq[sender.session_id] = sender.next_seq

        # Replay rejection: accept once, reject duplicate
        replay_intent = self.classifier.classify(fusion_frame, gesture="click")
        replay_ev = sender.emit(
            replay_intent.event_type,
            confidence=0.95,
            payload=replay_intent.payload,
            ts_ms=now,
        )
        now += 10
        self.ble.send(replay_ev)
        first = self.ble.recv()
        assert adapter.ingest(first, now_ms=now) is not None
        now += 5
        replay_reject = adapter.ingest(first, now_ms=now) is None
        report.exercised["replay"] = replay_reject
        if replay_reject:
            report.rejects.append({"gesture": "replay", "reason": "replay"})
            self.sink.reject("replay", first)

        # Lost / revoked ring
        adapter.receiver.revocation.revoke_device(sm.device_id)
        lost_ev = sender.emit("heartbeat", confidence=0.9, ts_ms=now + 20)
        self.ble.send(lost_ev)
        lost_pkt = self.ble.recv()
        lost_ok = adapter.ingest(lost_pkt, now_ms=now + 20) is None
        report.exercised["lost_ring"] = lost_ok
        if lost_ok:
            report.rejects.append({"gesture": "lost_ring", "reason": "revoked"})
            self.sink.reject("revoked", lost_pkt)
        adapter.receiver.expected_seq[sender.session_id] = sender.next_seq

        # Reconnect after link loss (fresh session)
        self.ble.lose_link()
        self.ble.reconnect()
        _sm2, sender2, adapter2, _ = self._pair_and_calibrate(now + 1000)
        recon_ev = sender2.emit(
            "pointer_move", confidence=0.92, payload={"dx": 1}, ts_ms=now + 1000
        )
        self.ble.send(recon_ev)
        recon_pkt = self.ble.recv()
        recon_action = adapter2.ingest(recon_pkt, now_ms=now + 1000)
        report.exercised["reconnect"] = recon_action is not None and self.ble.reconnects >= 1
        if recon_action:
            self.sink.route(
                {"kind": recon_action.kind, "event_type": recon_action.event_type},
                target="app",
            )

        required = [
            "keyboard",
            "pointer",
            "scroll",
            "click",
            "chord",
            "game_button",
            "analog",
            "destructive",
            "low_confidence_destructive",
            "replay",
            "lost_ring",
            "reconnect",
        ]
        missing = [k for k in required if not report.exercised.get(k)]
        stage_ok = all(
            report.stages.get(s)
            for s in (
                "fake_buses_firmware",
                "ble_sim",
                "gunnchos_ring_service",
                "calibration",
                "classifier",
                "input_routing",
                "app_game_feedback",
            )
        )
        report.ok = stage_ok and not missing
        if missing:
            report.errors.append("missing_exercises:" + ",".join(missing))
        return report


def main() -> int:
    import json

    report = RingEndToEndDigital().run()
    print(json.dumps(report.as_dict(), indent=2))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
