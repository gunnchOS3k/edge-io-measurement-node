# Field Test Protocol — Pixel 6a / MacBook

**Scope:** Exploratory, opt-in **phone-first field console** measurements for twin calibration research. **Not** a citywide campaign or carrier drive test.

---

## Equipment

| Role | Device | Notes |
|------|--------|-------|
| Primary handset | Google Pixel 6a | Consent UX + logging (web/APK planned) |
| Field laptop | MacBook | Probe orchestration, CSV export |
| Network | Public Wi-Fi or approved test AP | No credential harvesting |

---

## Pre-flight checklist

- [ ] Participant read and signed opt-in (adults) or guardian/program approval (minors)
- [ ] `consent_flag` enabled in logger
- [ ] Waypoint labels prepared (no raw GPS in public export)
- [ ] SDR (if any): receive-only, no transmission
- [ ] Screenshot folder created: `field_run_YYYYMMDD_waypoint/`

---

## Step-by-step procedure

1. **Label session:** `location_label=gene_waypoint_XX`, `gps_precision_bucket=coarse|none`.
2. **Baseline idle:** 3 repeated probe runs (`latency`, `jitter`, `packet_loss`) — wait 30 s between runs.
3. **Load scenario (optional):** light browsing or sanctioned speed test — **no third-party payload capture**.
4. **Record device status:** CPU, battery, temperature via `device_status_probe`.
5. **Offline AI check (optional):** run on-device model; log `offline_ai_latency_ms` only.
6. **Export:** merge probes → validate schema → write CSV/JSON.
7. **Screenshots to capture:**
   - Consent screen
   - Waypoint label visible
   - Export confirmation (no PII visible)
   - Optional speed-test summary (numbers only)
8. **Repeat discipline:** minimum **5 runs per waypoint**, 2+ waypoints per session.
9. **Post-session:** aggregate stats; delete raw logs per retention policy.

---

## Commands (MacBook developer path)

```bash
cd edge-io-measurement-node
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python3 -c "
from edge_io_node.probes import probe_latency, probe_jitter, probe_packet_loss, probe_rssi, probe_device_status
print(probe_latency()); print(probe_jitter()); print(probe_packet_loss()); print(probe_rssi()); print(probe_device_status())
"
make test
```

---

## What NOT to collect

- Packet payloads or DNS/HTTP contents
- SSID/BSSID tied to individuals
- Precise home addresses
- Screenshots with faces or student IDs
- Other users' traffic metadata beyond aggregate AP performance

---

## Evidence artifacts

Store under `results/field/` (gitignored if containing campaign IDs):

- `run_manifest.json` (seeds, waypoints, consent version)
- `telemetry_export.csv`
- Redacted screenshot index

Mark field results **`proven`** only after schema validation + privacy review.
