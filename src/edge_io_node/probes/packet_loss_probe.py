"""Packet-loss probe using repeated lightweight reachability checks."""
from __future__ import annotations

import platform
import socket
import time
from typing import Any


def probe_packet_loss(host: str = "1.1.1.1", port: int = 53, attempts: int = 5) -> dict[str, Any]:
    loss = 0
    for _ in range(max(attempts, 1)):
        try:
            with socket.create_connection((host, port), timeout=0.8):
                pass
        except OSError:
            loss += 1
        time.sleep(0.05)
    pct = round(100.0 * loss / max(attempts, 1), 3)
    return {
        "packet_loss_pct": pct,
        "notes_redacted": f"packet_loss_probe_attempts={attempts}; platform={platform.system()}",
    }
