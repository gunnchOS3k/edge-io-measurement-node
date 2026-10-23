"""Latency stub. The numeric zero is not a measured sample."""


def measure_latency_ms(host: str) -> dict:
    """Return a placeholder zero classified as unavailable.

    No probe is performed. The zero is not a physical or sensor measurement.
    """
    return {
        "host": host,
        "latency_ms": 0.0,
        "measurement_class": "unavailable",
        "physical_measurement": False,
        "sensor_reading": False,
    }
