# Edge IO — Privacy Digital Export Prep (Prompt 18)

**Evidence class:** `DRAFT_DIGITAL_CANDIDATE` for this packet; physical Ring remains `PHYSICAL_VALIDATION_PENDING`.

## What this closes digitally
- Denylist for common PII fields on research/campus export path.
- Consent-gated `transform_for_research_export`.
- `export_readiness_report` attestation with explicit `PHYSICAL_EVT_PASS=false`.

## What this does NOT claim
- Ring functional EVT PASS
- FCC/CE / battery / manufacturing
- Production telemetry from real users

## Verify
```bash
python -m pytest tests/test_privacy.py -q
```
