"""End-to-end measurement run over simulated ring sensor stream."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .latency_hooks import HarnessLatencyReport
from .validator import RingInputValidator, _load_reference_module


@dataclass
class RingInputMeasurementRun:
    """Produces software evidence for Gate 1 authenticated input."""

    def execute(self) -> dict[str, Any]:
        latency = HarnessLatencyReport()
        latency.mark("harness_start")
        validation = RingInputValidator().run()
        ari = _load_reference_module()
        stream = ari.SimulatedSensorStream()
        samples = stream.generate(n=8)
        latency.mark("harness_end", samples=len(samples))
        return {
            "validation": validation.to_dict(),
            "latency": latency.to_dict(),
            "simulated_sample_count": len(samples),
            "evidence_class": "SOFTWARE_SIMULATED",
            "physical_ring_claimed": False,
            "statuses": {
                "AUTHENTICATED_INPUT_PROTOCOL_PASS": validation.ok,
                "RING_PHYSICAL_PROTOTYPE_PENDING": True,
            },
        }
