"""Measurement / validation harness for authenticated ring input.

Hosts Gate 1 Workstream B validation pieces. Evidence is SOFTWARE_SIMULATED.
Physical ring: RING_PHYSICAL_PROTOTYPE_PENDING — not claimed.
"""

from .latency_hooks import HarnessLatencyReport
from .measurement_run import RingInputMeasurementRun
from .validator import RingInputValidator, ValidationReport

__all__ = [
    "HarnessLatencyReport",
    "RingInputMeasurementRun",
    "RingInputValidator",
    "ValidationReport",
]

STATUSES = {
    "AUTHENTICATED_INPUT_PROTOCOL_PASS": True,
    "RING_PHYSICAL_PROTOTYPE_PENDING": True,
}
PHYSICAL_RING_CLAIMED = False
