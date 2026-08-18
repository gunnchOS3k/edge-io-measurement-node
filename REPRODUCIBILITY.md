# Reproducibility — Edge-IO Measurement Node (RQ3)

This repository’s default path is **digital**: simulated device, consent, telemetry schema, privacy sanitization, anti-replay counters, and research export. It does **not** contain executed Pixel 6a field measurements in git.

Absolute spatial accuracy remains **PHYSICAL_PENDING**. IMU (ring classifier) is **relative cues only**, not validated absolute pose. No University of Oulu affiliation is claimed.

## Clone / setup / run

```bash
git clone https://github.com/gunnchOS3k/edge-io-measurement-node.git
cd edge-io-measurement-node
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make test
make smoke   # long e2e; synthetic only
make reproduce
```

Canonical independent digital path: `make reproduce`.

Physical Pixel 6a: follow `docs/PIXEL_6A_ACCEPTANCE.md` and `docs/PHYSICAL_CALIBRATION_PROCEDURE.md`. Do not label emulator output as physical.

## Expected outputs

- pytest passes on tests that do not require sibling hardware checkouts
- `python3 -m edge_io_node research-export --site gary` writes a synthetic pack with `spatial_accuracy: PHYSICAL_PENDING`
- Firmware host-sim / MCUboot tests remain `SOFTWARE_SIMULATED`

## Tool versions

| Tool | Version guidance |
|------|------------------|
| Python | 3.10+ |
| Android SDK / Gradle | optional; required only for APK |

## Evidence discipline

**Real today:** schemas, consent lifecycle, emulator collector, privacy filters, anti-replay helper, firmware digital sim.

**Synthetic / demo-only:** emulator latency/jitter series, research export JSON.

**Planned / PHYSICAL_PENDING:** Pixel 6a QoS sessions, absolute spatial accuracy.

**Not claimed:** validated absolute IMU pose; Oulu affiliation; RF campaign measurements.
