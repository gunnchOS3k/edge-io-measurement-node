# Physical calibration procedure (exact)

**Status of execution in this repository:** `PHYSICAL_PENDING`

This procedure is the **only** accepted path to lift IMU/spatial claims above relative software cues. Until a signed calibration record exists under `physical_evidence/`, IMU outputs remain `relative_cues_only_not_absolute_pose` and absolute spatial accuracy remains `PHYSICAL_PENDING`.

Do not invent numbers. If a step is skipped, stop and keep `PHYSICAL_PENDING`.

## Equipment

1. Google Pixel 6a with the Edge-IO Android client (`clients/android`) installed from a recorded APK SHA-256.
2. Optional research ring (hardware sibling) **only if** a fabricated unit is in hand. If no ring is present, skip ring IMU steps; do not substitute firmware-host-sim values.
3. Rigid table, spirit level, tape measure (≥ 2 m), right-angle square.
4. Printed axis card: +X, +Y, +Z marked in millimetres.
5. Notebook or `physical_evidence/CALIBRATION_RECORD_TEMPLATE.json` copy named with date and device serial **hash** (not raw serial in public git).

## Pre-conditions

1. Operator reads `docs/CONTROLLED_DEVICE_MEASUREMENT_PROTOCOL.md`.
2. Affirmative consent is captured in-app (or CLI `--consent` is **not** used as a substitute for a human Pixel session).
3. Location is a named test zone only (no residential address, no precise GPS).
4. Airplane mode off; Wi-Fi SSID/BSSID are **not** recorded.

## Pixel 6a network/QoS calibration (application layer)

1. Place the Pixel 6a flat, screen up, 1.00 m ± 0.02 m from the AP or Ethernet-bridged Wi-Fi endpoint used for the test. Photograph the tape measure in frame; store hash-named privately, not in git if the photo shows a room.
2. Open the Android client. Select **CALIBRATION** (`SessionMode.CALIBRATION`, 60 s).
3. Affirm consent. Start the 60-second calibration session.
4. Repeat **three** times on `wifi_normal`. Export each session JSON.
5. Repeat **three** times on `cellular_normal` if a SIM is lawfully available; otherwise record `cellular: not_executed` and keep those metrics unavailable.
6. Validate each JSON with `python3 -m edge_io_node validate <file> --schema-dir <field-kit contracts>`.
7. Fill `physical_evidence/CALIBRATION_RECORD_TEMPLATE.json`: device_category=`phone`, model_label=`pixel_6a`, evidence_level=`controlled_device_measurement`. Leave throughput/RSSI null if the unprivileged API did not expose them.

## IMU / pose (ring or phone) — relative only unless this subsection is completed

Absolute pose is **not** claimed by software simulation.

If a physical IMU is present:

1. Mount the device on the levelled table. Record gravity vector mean over 30 s while stationary (`ax, ay, az` in device coordinates). Expected magnitude ≈ 9.81 m/s² ± device spec; **do not** convert this into a map pose.
2. Rotate +90° about device X, then Y, then Z, pausing 10 s each. Record that the dominant axis changes sign/magnitude as expected. This is **axis identity**, not georeferenced pose.
3. Translate the device 1.00 m along table +X at walking speed. Record that integrated acceleration is **not** used as a validated 1.00 m displacement. Write `spatial_accuracy: PHYSICAL_PENDING` unless an independent optical or tape-verified tracking system is used in the same take.
4. To lift `PHYSICAL_PENDING` on absolute spatial accuracy, a second metrology source (e.g. tape-verified waypoints or a lab motion-capture system) must agree within a stated error bound recorded in the calibration JSON. **This repo does not currently contain that second source.**

## Ring firmware (only with hardware)

1. Confirm the unit matches `gate1_digital_fabrication` pinout notes.
2. Host-sim and MCUboot anti-replay tests are **software**. They do not calibrate a physical IMU.
3. Do not copy `host_sim` fusion frames into `physical_evidence/`.

## Stop conditions

- Consent withdrawn → delete session; do not export.
- Any metric unavailable → record reason; do not invent.
- No Pixel 6a present → entire physical path remains `PHYSICAL_PENDING`.
