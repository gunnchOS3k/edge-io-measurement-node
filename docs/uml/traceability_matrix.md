# Traceability matrix — edge-io-measurement-node

| Diagram element | Source path |
|-----------------|-------------|
| CLI collect | `src/edge_io_node/cli.py` |
| Consent | `src/edge_io_node/consent/lifecycle.py` |
| Collectors | `src/edge_io_node/collectors/base.py` |
| Schema | `src/edge_io_node/telemetry_schema.py` |
| Privacy | `src/edge_io_node/privacy.py` |
| Anti-replay | `src/edge_io_node/anti_replay.py`, firmware MCUboot pipeline |
| IMU non-claim | `src/edge_io_node/ring_e2e/classifier.py` |
| Android | `clients/android/app/src/main/java/org/gunnchos/edgeio/*` |
| Pixel 6a | `docs/PIXEL_6A_ACCEPTANCE.md` |
| Calibration | `docs/PHYSICAL_CALIBRATION_PROCEDURE.md` |

[← UML README](README.md)
