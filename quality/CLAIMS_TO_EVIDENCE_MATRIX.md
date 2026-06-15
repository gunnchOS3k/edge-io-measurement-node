# Claims to Evidence — edge-io-measurement-node

Statuses: `proven` | `synthetic-only` | `planned` | `not claimed`

| Claim | Status | Evidence (file / test / figure) | Limitation |
|-------|--------|----------------------------------|------------|
| Repository tests pass | proven | `make test`, 15 pytest cases | Smoke + unit |
| Telemetry schema documented | proven | `docs/TELEMETRY_SCHEMA.md`, `examples/sample_telemetry.*` | Synthetic examples |
| Schema validation blocks non-consent export | proven | `tests/test_telemetry_schema.py` | Unit test |
| No raw PII in export | proven | `FORBIDDEN_PII_FIELDS`, `tests/test_telemetry_schema.py` | Field name guard |
| Modular probes return structured dicts | proven | `src/edge_io_node/probes/`, `tests/test_probes.py` | Platform fallbacks |
| Privacy sanitize strips unknown fields | proven | `tests/test_privacy.py` | Allow-list |
| Synthetic emulator + demo export | synthetic-only | `make smoke`, `results/e2e/` | Not field data |
| Pixel 6a / MacBook field protocol | proven | `docs/FIELD_TEST_PROTOCOL.md` | Procedure only |
| Android APK field console | planned | `docs/ANDROID_FIELD_CONSOLE_ROADMAP.md` | Not shipped |
| Citywide representative sampling | not claimed | `docs/PRIVACY_AND_ETHICS.md` | Exploratory framing |
| Carrier-grade monitoring | not claimed | README non-claims | — |
| Unauthorized RF transmission | not claimed | Receive-only note in ethics doc | — |
| Twin calibration with live RAN | planned | Link to spectrumx-ai-ran-gary | Integration TBD |
