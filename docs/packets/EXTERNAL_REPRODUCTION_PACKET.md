# External / independent reproduction packet — edge-io-measurement-node

**Status:** `INDEPENDENT_REPRODUCTION_PENDING` for a second-person sign-off. The **digital command path** is ready. Physical Pixel 6a remains `PHYSICAL_PENDING`.

Cursor cannot sign this on another person’s behalf.

## Digital command

```bash
git clone https://github.com/gunnchOS3k/edge-io-measurement-node.git
cd edge-io-measurement-node
git checkout <frozen-sha>
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make test
make reproduce
```

Some CI jobs check out sibling repos (`gunnchos-device-os`, hardware, field-kit). Independent digital PASS for RQ3 in this packet is the **stdlib Python path** (`tests/test_rq3_digital_measurement.py`, `tests/test_telemetry_schema.py`, `tests/test_privacy.py`, research-export). Sibling-dependent ring E2E may be skipped if siblings are absent; record the skip.

## Expected evidence form

```text
system:
commit:
command: make reproduce
start:
end:
result:
output_hashes:
deviations:
PASS_FAIL:
notes: synthetic only; spatial_accuracy PHYSICAL_PENDING; IMU not absolute pose; not Oulu affiliation
```

## Physical path (separate)

Follow `docs/PIXEL_6A_ACCEPTANCE.md`. Do not treat digital PASS as Pixel 6a acceptance.
