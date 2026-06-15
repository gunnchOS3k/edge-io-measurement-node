# Telemetry Schema — Edge-IO Measurement Node

Privacy-preserving, **opt-in** telemetry for exploratory field measurements. This schema supports **phone-first field console** logging aligned with IMT-2030 digital-twin calibration research. It does **not** authorize packet payload capture or third-party traffic inspection.

Implementation: `src/edge_io_node/telemetry_schema.py`

---

## Fields

| Field | Type | Required on export | Notes |
|-------|------|--------------------|-------|
| `timestamp_utc` | ISO-8601 string | yes | UTC only |
| `device_id_hash` | string | yes | Pseudonymous hash ≥ 8 chars |
| `location_label` | string | yes | Waypoint label, not raw GPS |
| `gps_precision_bucket` | enum | yes | `none`, `coarse`, `medium`, `fine` |
| `network_type` | string | yes | e.g., `wifi`, `cellular`, `unknown` |
| `rssi_dbm` | float | no | Platform-dependent |
| `latency_ms` | float | no | Active probe latency |
| `jitter_ms` | float | no | Derived from repeated probes |
| `packet_loss_pct` | float | no | 0–100 |
| `download_mbps` | float | no | Throughput test result |
| `upload_mbps` | float | no | Throughput test result |
| `cpu_pct` | float | no | Device CPU load |
| `battery_pct` | float | no | Battery level |
| `device_temp_c` | float | no | Optional sensor |
| `offline_ai_latency_ms` | float | no | On-device inference latency |
| `consent_flag` | bool | yes | Must be true to export |
| `notes_redacted` | string | no | Operator notes without PII |

**Forbidden fields (never store/export):** email, phone, IMEI, MAC, SSID, BSSID, raw lat/lon, student IDs, IP addresses.

---

## JSON example

See `examples/sample_telemetry.json`.

```json
{
  "timestamp_utc": "2026-06-15T18:30:00Z",
  "device_id_hash": "sha256_demo_device_001",
  "location_label": "gary_library_waypoint_a",
  "gps_precision_bucket": "coarse",
  "network_type": "wifi",
  "rssi_dbm": -62.0,
  "latency_ms": 18.4,
  "jitter_ms": 2.1,
  "packet_loss_pct": 0.0,
  "download_mbps": 42.5,
  "upload_mbps": 8.2,
  "cpu_pct": 21.0,
  "battery_pct": 78.0,
  "device_temp_c": 32.5,
  "offline_ai_latency_ms": 95.0,
  "consent_flag": true,
  "notes_redacted": "synthetic_example_record; no payload capture"
}
```

---

## CSV example

See `examples/sample_telemetry.csv`.

```csv
timestamp_utc,device_id_hash,location_label,gps_precision_bucket,network_type,rssi_dbm,latency_ms,jitter_ms,packet_loss_pct,download_mbps,upload_mbps,cpu_pct,battery_pct,device_temp_c,offline_ai_latency_ms,consent_flag,notes_redacted
2026-06-15T18:30:00Z,sha256_demo_device_001,gary_library_waypoint_a,coarse,wifi,-62.0,18.4,2.1,0.0,42.5,8.2,21.0,78.0,32.5,95.0,true,synthetic_example_record; no payload capture
```

---

## Data minimization notes

1. Use **waypoint labels** instead of precise coordinates in public exports.
2. Hash device identifiers; rotate salts per campaign when feasible.
3. Export only fields needed for aggregated analysis.
4. Block export unless `consent_flag` is true (or legacy `opt_in` / `consent_state=opt_in_active`).
5. Apply `privacy.sanitize()` before 7GC export.
6. Default retention: delete raw logs after export in toy mode (`retention_policy`).

---

## Probes

Modular probes in `src/edge_io_node/probes/` return partial dicts mergeable into a full record:

- `latency_probe.py`
- `packet_loss_probe.py`
- `jitter_probe.py`
- `rssi_probe.py`
- `device_status_probe.py`

Each probe uses **safe fallbacks** when OS APIs are unavailable.
