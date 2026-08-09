"""Target app/game feedback sink for ring E2E digital scenario."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AppGameFeedback:
    app_id: str = "waike-learning"
    game_id: str = "anime-aggressors"
    accepted: list[dict[str, Any]] = field(default_factory=list)
    rejected: list[dict[str, Any]] = field(default_factory=list)
    feedback: list[dict[str, Any]] = field(default_factory=list)

    def route(self, action: dict[str, Any], *, target: str = "app") -> dict[str, Any]:
        sink = {
            "target": target,
            "app_id": self.app_id if target == "app" else None,
            "game_id": self.game_id if target == "game" else None,
            "action": action,
            "ack": True,
        }
        self.accepted.append(sink)
        haptic = {
            "type": "haptic_pulse",
            "ms": 20 if action.get("kind") != "noop" else 0,
            "for_action": action.get("kind"),
        }
        self.feedback.append(haptic)
        return sink

    def reject(self, reason: str, raw: dict[str, Any] | None = None) -> dict[str, Any]:
        item = {"reason": reason, "raw": raw or {}, "ack": False}
        self.rejected.append(item)
        self.feedback.append({"type": "reject_beep", "reason": reason})
        return item
