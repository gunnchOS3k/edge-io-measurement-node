"""Ring end-to-end digital input pipeline (Continuation VII §19).

fake buses → firmware fusion logic → auth packet → BLE sim →
gunnchOS ring service → calibration → classifier → input routing →
app/game → feedback.

Earns: RING_END_TO_END_DIGITAL_INPUT_PASS (digital only).
Physical accuracy/latency remains RING_PHYSICAL_BOOT_PENDING.
"""

from __future__ import annotations

from .pipeline import RingEndToEndDigital, E2EReport
from .tokens import E2E_TOKEN, PHYSICAL_TOKEN, STATUSES

__all__ = [
    "RingEndToEndDigital",
    "E2EReport",
    "E2E_TOKEN",
    "PHYSICAL_TOKEN",
    "STATUSES",
]
