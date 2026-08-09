"""Continuation VII E2E status tokens."""

E2E_TOKEN = "RING_END_TO_END_DIGITAL_INPUT_PASS"
PHYSICAL_TOKEN = "RING_PHYSICAL_BOOT_PENDING"

STATUSES = {
    E2E_TOKEN: False,  # set True only after pipeline report.ok
    PHYSICAL_TOKEN: True,
    "PHYSICAL_ACCURACY_LATENCY_PENDING": True,
}
