# Pixel 6a acceptance — digital criteria

**Physical execution status:** `PHYSICAL_PENDING`

The Android client under `clients/android` **targets** Pixel 6a. This document is the acceptance checklist. It is **not** a signed lab report that a Pixel 6a session was collected.

Related: `docs/CONTROLLED_DEVICE_MEASUREMENT_PROTOCOL.md`, `docs/PHYSICAL_CALIBRATION_PROCEDURE.md`.

## In-scope client behavior (code exists)

| Item | Where | Pass criterion (digital) |
|------|--------|---------------------------|
| Consent gate | `ConsentManager.kt` | Collection cannot start without affirmative opt-in |
| Session modes | `SessionMode.kt` | CALIBRATION 60 s; PILOT/REHEARSAL 300 s |
| No GPS / identifiers | `PhysicalMetricsSampler.kt` | Comments and unavailable map forbid GPS, SSID, BSSID, MAC, IMEI, IMSI |
| Unprivileged metrics only | `PhysicalMetricsSampler.kt` | Throughput, packet loss, RSSI, CPU recorded as unavailable when APIs are not exposed |
| Export | `SessionExporter.kt` | Session JSON can be written for host validation |

## Out of scope until physical evidence exists

| Item | Status |
|------|--------|
| Application-layer latency on a real Pixel 6a | PHYSICAL_PENDING |
| Absolute IMU pose | **Never** claimed from this client; IMU is not sampled here |
| RF lab RSSI / channel sounding | NOT COLLECTED (and must not be invented) |
| Independent reproduction on a second Pixel 6a | PENDING |

## Build (when Android SDK is available)

```bash
make android-debug-apk
make android-test
```

If Gradle/SDK is missing, document skip — do not treat skip as physical PASS.

## Acceptance decision rule

A Pixel 6a session may be labeled `evidence_level: controlled_device_measurement` **only if**:

1. JSON was generated on-device (not `DeterministicEmulatorCollector`).
2. Consent receipt is present.
3. Unavailable metrics are null/flagged, not fabricated.
4. `docs/PHYSICAL_CALIBRATION_PROCEDURE.md` steps 1–7 for QoS calibration were followed.

Until then, keep `SYNTHETIC TEST MODE` labels.
