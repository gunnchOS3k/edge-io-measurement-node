# Controlled Device Measurement Protocol

This protocol produces **controlled_device_measurement** evidence for Gate 2.
It does **not** recruit participants and must not capture residential addresses,
precise GPS, or third-party personal data.

## Scope

- Devices: Pixel 6a; one laptop
- Networks: Wi-Fi; cellular; intentionally degraded local-network conditions
- Workloads: Learn, Create, Sense
- Repetitions: at least three per condition
- Identifiers: stable non-identifying session IDs / consent receipts only

## Consent

1. Display the plain-language collection summary in the Android client (or laptop CLI wrapper).
2. Require affirmative opt-in before any collection.
3. Record a non-identifying consent receipt.
4. Allow stop, export, delete, and withdrawal at any time.

## Exact commands (laptop / emulator path for automation)

Synthetic (labeled `evidence_level=synthetic`) — for CI only:

```bash
cd edge-io-measurement-node
PYTHONPATH=src python3 -m edge_io_node collect \
  --profile learn \
  --duration 90 \
  --interval 30 \
  --site gary \
  --run-id 2026-07-22-synthetic-gary-learn-001 \
  --output results/session.json \
  --consent \
  --collector emulator

PYTHONPATH=src python3 -m edge_io_node validate \
  results/session.json \
  --schema-dir ../gunnchos-7gc-ai-ran-field-kit/contracts

PYTHONPATH=src python3 -m edge_io_node export-to-7gc \
  results/session.json \
  --output results/01_edge_measurements.json \
  --schema-dir ../gunnchos-7gc-ai-ran-field-kit/contracts
```

## Exact commands (physical Pixel 6a)

1. Build/install the Android client under `clients/android`.
2. Affirm consent in-app.
3. Run Learn / Create / Sense for each network condition (≥3 reps).
4. Export session JSON from the app to the host.
5. Validate and place under field-kit `fixtures/controlled/` **only if** the file was device-generated:

```bash
PYTHONPATH=src python3 -m edge_io_node validate \
  /path/to/pixel6a_session_001.json \
  --schema-dir ../gunnchos-7gc-ai-ran-field-kit/contracts

cp /path/to/pixel6a_session_001.json \
  ../gunnchos-7gc-ai-ran-field-kit/fixtures/controlled/pixel6a_session_001.json
```

Physical collector via CLI (fails closed when no device is attached):

```bash
PYTHONPATH=src python3 -m edge_io_node collect \
  --profile learn \
  --duration 300 \
  --site gary \
  --run-id 2026-08-15-pixel6a-wifi-001 \
  --output results/session.json \
  --consent \
  --collector physical
```

## Degraded local conditions

On the laptop path, induce controlled degradation (example):

```bash
# Example only — operator chooses a local traffic-control tool they control.
# Do not capture third-party traffic or residential addresses.
```

Record the degradation method in the session provenance notes.

## Honesty rule

Do not claim this protocol was executed unless the JSON was generated from a physical device
and labeled `evidence_level: controlled_device_measurement`.
