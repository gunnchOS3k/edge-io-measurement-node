"""Device status probe (CPU, battery, temperature) with safe fallbacks."""
from __future__ import annotations

import platform
from typing import Any


def _read_battery_pct() -> float | None:
    if platform.system() != "Darwin":
        return None
    try:
        import subprocess

        out = subprocess.check_output(["pmset", "-g", "batt"], text=True, timeout=2.0)
        for token in out.replace("\t", " ").split():
            if token.endswith("%"):
                return float(token.rstrip("%"))
    except (OSError, ValueError, ImportError):
        return None
    return None


def probe_device_status() -> dict[str, Any]:
    cpu_pct = None
    battery_pct = _read_battery_pct()
    device_temp_c = None
    try:
        import psutil  # optional dependency

        cpu_pct = round(float(psutil.cpu_percent(interval=0.1)), 2)
        temps = getattr(psutil, "sensors_temperatures", lambda: {})()
        if temps:
            first = next(iter(temps.values()))
            if first:
                device_temp_c = round(float(first[0].current), 2)
    except Exception:
        cpu_pct = cpu_pct or None

    return {
        "cpu_pct": cpu_pct,
        "battery_pct": battery_pct,
        "device_temp_c": device_temp_c,
        "notes_redacted": f"device_status_probe; platform={platform.system()}",
    }
