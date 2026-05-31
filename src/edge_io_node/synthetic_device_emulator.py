def emulate_sample(device_id_hash: str) -> dict:
    return {
        "device_id_hash": device_id_hash,
        "timestamp_iso": "2026-01-01T12:00:00Z",
        "consent_state": "opt_in_active",
        "latency_ms": 12.0,
        "jitter_ms": 1.5,
        "packet_loss_percent": 0.1,
        "cpu_percent": 22.0,
        "memory_percent": 41.0,
        "privacy_tier": "synthetic_tier_a",
        "retention_policy": "delete_after_export_toy",
        "opt_in": True,
    }


def emulate_samples(n: int = 5) -> list[dict]:
    return [emulate_sample(f"hash_{i:04d}") for i in range(n)]
