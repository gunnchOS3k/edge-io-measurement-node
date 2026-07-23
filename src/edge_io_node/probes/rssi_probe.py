"""RSSI probe with platform-safe fallback (no raw Wi-Fi scan payloads)."""
from __future__ import annotations

import platform
import subprocess
from typing import Any


def probe_rssi() -> dict[str, Any]:
    system = platform.system()
    if system == "Darwin":
        try:
            out = subprocess.check_output(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=2.0,
            )
            for line in out.splitlines():
                if "agrCtlRSSI" in line or "RSSI" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        value = parts[1].strip().split()[0]
                        return {
                            "rssi_dbm": float(value),
                            "network_type": "wifi",
                            "notes_redacted": "rssi_probe_darwin_airport",
                        }
        except (OSError, subprocess.SubprocessError, ValueError):
            pass
    return {
        "rssi_dbm": None,
        "network_type": "unknown",
        "notes_redacted": f"rssi_unavailable; platform={system}",
    }
