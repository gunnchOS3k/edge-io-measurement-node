"""Latency hooks for ring-input measurement harness."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class HarnessLatencyReport:
    """Software-path latency samples. Not physical RF/sensor latency."""

    evidence_class: str = "SOFTWARE_SIMULATED"
    physical_ring_claimed: bool = False
    marks: list[dict[str, Any]] = field(default_factory=list)

    def mark(self, stage: str, **meta: Any) -> None:
        self.marks.append({"stage": stage, "t": time.perf_counter(), **meta})

    def delta_ms(self, a: str, b: str) -> float | None:
        sa = next((m for m in reversed(self.marks) if m["stage"] == a), None)
        sb = next((m for m in reversed(self.marks) if m["stage"] == b), None)
        if not sa or not sb:
            return None
        return (sb["t"] - sa["t"]) * 1000.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "encode_to_verify_ms": self.delta_ms("harness_start", "harness_end"),
            "mark_count": len(self.marks),
            "evidence_class": self.evidence_class,
            "physical_ring_claimed": self.physical_ring_claimed,
        }
