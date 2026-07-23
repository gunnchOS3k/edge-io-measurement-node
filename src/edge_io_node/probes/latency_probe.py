"""Latency probe with safe fallbacks when OS/network APIs are unavailable."""
from __future__ import annotations

import platform
import socket
import time
from typing import Any


def probe_latency(host: str = "1.1.1.1", port: int = 53, timeout_s: float = 1.0) -> dict[str, Any]:
    start = time.perf_counter()
    ok = False
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            ok = True
    except OSError:
        ok = False
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return {
        "latency_ms": round(elapsed_ms, 3) if ok else None,
        "network_type": "unknown",
        "notes_redacted": f"latency_probe_ok={ok}; platform={platform.system()}",
    }
