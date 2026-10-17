# Measurement plan — graham_land

```json
{
  "site_id": "graham_land",
  "mode": "local-safe",
  "allowed": [
    "latency_ms",
    "jitter_ms",
    "packet_loss_pct",
    "throughput_mbps_stub"
  ],
  "prohibited": [
    "precise_gps",
    "contact_list",
    "message_content",
    "biometrics"
  ],
  "consent_mode": "explicit_opt_in",
  "privacy_tier": "aggregate_only",
  "evidence_status": "smoke_test_only",
  "needs_local_validation": true
}
```
