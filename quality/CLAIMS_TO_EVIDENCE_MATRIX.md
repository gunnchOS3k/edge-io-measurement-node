# Claims to evidence — edge-io-measurement-node

RQ3 digital measurement/firmware paths. No invented RF or device campaign numbers.

| Claim | Evidence level | Artifact | Status |
|-------|----------------|----------|--------|
| Consent-gated synthetic collection | 2 digital | `consent/lifecycle.py`, CLI `--consent` | PASS digital |
| Telemetry schema + privacy sanitize | 2 digital | `telemetry_schema.py`, `privacy.py` | PASS digital |
| Anti-replay counters (telemetry + firmware sim) | 2 software | `anti_replay.py`, MCUboot pipeline | PASS digital |
| Research export with provenance | 2 synthetic | `research_export.py` | PASS digital |
| IMU not absolute pose | 2 documented | `ring_e2e/classifier.py` `pose_claim` | PASS digital |
| Absolute spatial accuracy | PHYSICAL_PENDING | `docs/PHYSICAL_CALIBRATION_PROCEDURE.md` | PENDING |
| Pixel 6a physical QoS | PHYSICAL_PENDING | `docs/PIXEL_6A_ACCEPTANCE.md` | PENDING |
| Independent second-person digital reproduction | pending | `docs/packets/EXTERNAL_REPRODUCTION_PACKET.md` | PENDING |
| Oulu affiliation | not claimed | README | NOT CLAIMED |
