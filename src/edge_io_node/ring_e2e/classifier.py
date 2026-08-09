"""Spatial / input classifier over ring fusion frames (software-simulated)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ClassifiedIntent:
    event_type: str
    confidence: float
    payload: dict[str, Any]
    destructive: bool = False


class SpatialInputClassifier:
    """Maps IMU/cap fusion cues to OS/game input intents."""

    def classify(self, frame: dict[str, Any], *, gesture: str | None = None) -> ClassifiedIntent:
        if gesture:
            return self._from_gesture(gesture, frame)
        ax = float(frame.get("ax", 0.0))
        ay = float(frame.get("ay", 0.0))
        gz = float(frame.get("gz", 0.0))
        touch = bool(frame.get("cap_touch", False))
        cal = float(frame.get("cal_conf", 0.0))
        base_conf = 0.55 + 0.4 * cal

        if abs(gz) > 0.8 and touch:
            return ClassifiedIntent("scroll", min(1.0, base_conf + 0.1), {"dy": int(gz * 10)})
        if abs(ax) > 0.4 or abs(ay) > 0.4:
            return ClassifiedIntent(
                "pointer_move",
                base_conf,
                {"dx": int(ax * 20), "dy": int(ay * 20)},
            )
        if touch:
            return ClassifiedIntent("click", base_conf, {"button": 1})
        return ClassifiedIntent("heartbeat", max(0.5, base_conf - 0.2), {})

    def _from_gesture(self, gesture: str, frame: dict[str, Any]) -> ClassifiedIntent:
        cal = float(frame.get("cal_conf", 1.0))
        conf = 0.6 + 0.35 * cal
        table = {
            "keyboard": ClassifiedIntent("key_press", conf, {"key": "a"}),
            "key_release": ClassifiedIntent("key_release", conf, {"key": "a"}),
            "pointer": ClassifiedIntent("pointer_move", conf, {"dx": 5, "dy": -2}),
            "scroll": ClassifiedIntent("scroll", conf, {"dy": -3}),
            "click": ClassifiedIntent("click", conf, {"button": 1}),
            "chord": ClassifiedIntent(
                "key_press",
                conf,
                {"key": "s", "modifiers": ["ctrl"]},
            ),
            "game_button": ClassifiedIntent(
                "click",
                conf,
                {"button": 1, "game_action": "jump"},
            ),
            "analog": ClassifiedIntent(
                "pointer_move",
                conf,
                {"dx": 12, "dy": 0, "analog": True, "axis": "lx"},
            ),
            "destructive": ClassifiedIntent(
                "destructive_confirm",
                conf,
                {"action": "delete"},
                destructive=True,
            ),
            "low_confidence_destructive": ClassifiedIntent(
                "destructive_confirm",
                0.3,
                {"action": "delete"},
                destructive=True,
            ),
        }
        if gesture not in table:
            raise ValueError(f"unknown gesture {gesture}")
        return table[gesture]
