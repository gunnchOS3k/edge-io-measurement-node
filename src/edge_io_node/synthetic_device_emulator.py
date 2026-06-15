def emulate_sample(device_id_hash: str) -> dict:
    return {
        "device_id_hash": device_id_hash,
        "timestamp_utc": "2026-01-01T12:00:00Z",
        "timestamp_iso": "2026-01-01T12:00:00Z",
        "location_label": "synthetic_waypoint",
        "gps_precision_bucket": "none",
        "network_type": "wifi",
        "consent_state": "opt_in_active",
        "consent_flag": True,
        "latency_ms": 12.0,
        "jitter_ms": 1.5,
        "packet_loss_pct": 0.1,
        "packet_loss_percent": 0.1,
        "cpu_pct": 22.0,
        "cpu_percent": 22.0,
        "memory_percent": 41.0,
        "privacy_tier": "synthetic_tier_a",
        "retention_policy": "delete_after_export_toy",
        "opt_in": True,
        "notes_redacted": "synthetic_emulator_record",
    }


def emulate_samples(n: int = 5) -> list[dict]:
    return [emulate_sample(f"hash_{i:04d}") for i in range(n)]
