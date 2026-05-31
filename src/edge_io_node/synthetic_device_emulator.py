def emulate_sample(device_id_hash: str) -> dict:
    return {
        "device_id_hash": device_id_hash,
        "timestamp_iso": "2026-01-01T12:00:00Z",
        "latency_ms": 12.0,
        "jitter_ms": 1.5,
        "packet_loss_pct": 0.1,
        "opt_in": True,
    }


def emulate_samples(n: int = 5) -> list[dict]:
    return [emulate_sample(f"hash_{i:04d}") for i in range(n)]
