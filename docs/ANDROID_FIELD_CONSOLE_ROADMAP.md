# Android Field Console Roadmap — Phone-First Measurement Kit

Minimal plan for a **phone-first field console** aligned with IMT-2030 exploratory measurements. This is a **research prototype**, not a commercial 6G app.

---

## Phase 0 — Mobile web (MVP)

| Item | Detail |
|------|--------|
| Stack | Static PWA or lightweight React/Vite shell |
| Logging | IndexedDB offline queue |
| Probes | Browser-available APIs only (latency fetch, Network Information where exposed) |
| Consent | Blocking modal → sets `consent_flag` |
| Export | CSV download + optional QR for laptop import |
| Privacy | No payload capture; waypoint labels typed by operator |

**Deliverable:** hosted demo + `docs/FIELD_TEST_PROTOCOL.md` compatibility.

---

## Phase 1 — Minimal APK (Android)

| Item | Detail |
|------|--------|
| Stack | Kotlin + Jetpack Compose or Capacitor wrapper |
| Offline-first | Room/SQLite queue; sync when Wi-Fi available |
| Probes | Android ConnectivityManager signal strength (where permitted), foreground speed test module |
| Export | Share sheet CSV; USB adb pull for lab |
| Privacy-preserving sync | Aggregates only to server; E2E optional later |

**Non-goals:** root-only RF hooks, background sniffing, non-consensual logging.

---

## Phase 2 — Twin calibration hook

- Map `location_label` → campus YAML profile (Gary anchor).
- Push sanitized aggregates to 7GC export contract (`seven_gc_export.json` shape).
- Pair with `spectrumx-ai-ran-gary` synthetic twin for **calibration experiments** (planned evidence).

---

## Phase 3 — Governance

- School/program IRB or equivalent review
- Retention/deletion UI
- Participant withdrawal ("delete my device hash" flow)

---

## Success criteria

- [ ] Offline logging survives airplane mode
- [ ] CSV matches `docs/TELEMETRY_SCHEMA.md`
- [ ] `tests/test_telemetry_schema.py` passes on exported samples
- [ ] Public docs state **what is real vs planned**
