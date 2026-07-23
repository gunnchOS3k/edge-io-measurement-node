"""Jitter probe derived from repeated latency samples."""
from __future__ import annotations

import statistics
from typing import Any

from .latency_probe import probe_latency


def probe_jitter(samples: int = 5) -> dict[str, Any]:
    latencies: list[float] = []
    for _ in range(max(samples, 2)):
        sample = probe_latency()
        if sample.get("latency_ms") is not None:
            latencies.append(float(sample["latency_ms"]))
    if len(latencies) < 2:
        return {"jitter_ms": None, "notes_redacted": "jitter_probe_insufficient_samples"}
    jitter = statistics.pstdev(latencies)
    return {"jitter_ms": round(jitter, 3), "notes_redacted": f"jitter_probe_samples={len(latencies)}"}
