"""Monotonic anti-replay for synthetic/digital telemetry sessions.

Firmware MCUboot anti-replay lives under gate1_digital_fabrication.
This module covers research-export telemetry counters — not a radio protocol.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class ReplayRejected(ValueError):
    pass


@dataclass
class AntiReplayWindow:
    seen: set[int] = field(default_factory=set)
    last: int = -1

    def accept(self, counter: int) -> bool:
        if counter < 0 or counter in self.seen or counter <= self.last:
            return False
        self.seen.add(counter)
        self.last = counter
        return True

    def require(self, counter: int) -> None:
        if not self.accept(counter):
            raise ReplayRejected(f"replay or out-of-order counter={counter} last={self.last}")


def stamp_sample(sample: dict, counter: int, nonce: str) -> dict:
    out = dict(sample)
    out["anti_replay_counter"] = int(counter)
    out["anti_replay_nonce"] = nonce
    return out
