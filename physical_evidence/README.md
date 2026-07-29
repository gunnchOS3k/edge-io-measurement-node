# Physical evidence (Gate 6 harness)

Templates and synthetic dry-run fixtures for Edge-IO field sessions.

- **Design reference:** sibling field-kit 54-cell matrix at `../gunnchos-7gc-ai-ran-field-kit/protocols/controlled_pilot_matrix.csv`
- **Synthetic only:** `fixtures/synthetic_session_dry_run.json` is labeled `SYNTHETIC_EXPERIMENT` / `DRY_RUN`
- **Quarantine:** invalid sessions go under `quarantine/` (never promote without re-validation)
- **Run:** `make gate6-dry-run` → `GATE6_DRY_RUN_REPORT.json`

Physical field pilot remains `FIELD_PILOT_PENDING` until controlled-device measurements exist.
