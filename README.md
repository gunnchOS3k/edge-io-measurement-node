# edge-io-measurement-node

Ring / Edge I/O **sensing and measurement** stack for gunnchOS3k — privacy-first telemetry, firmware paths, and Lab-facing contracts.

| Item | Detail |
|------|--------|
| **Runs today** | Research prototype with smoke test (synthetic, non-evidence) |
| **Demo** | `make smoke` (smoke test only — not readiness proof) |
| **Reproduce** | `make reproduce` — synthetic RQ3 path; see [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| **UML** | [docs/uml/README.md](docs/uml/README.md) |
| **Pixel 6a** | [docs/PIXEL_6A_ACCEPTANCE.md](docs/PIXEL_6A_ACCEPTANCE.md) (`PHYSICAL_PENDING`) |
| **Data** | Synthetic only — no private IQ or PII |
| **Extend** | See [EXTERNAL_RESEARCHER_QUICKSTART.md](docs/EXTERNAL_RESEARCHER_QUICKSTART.md) |
| **Limits** | Not operational 6G; not Oulu affiliation; not carrier-grade |
| **Readiness** | [END_TO_END_READINESS.md](docs/END_TO_END_READINESS.md) |
| **Smoke test** | [E2E_RUN_RECORD.md](reproducibility/E2E_RUN_RECORD.md) |
| **Artifacts** | [results/e2e/](results/e2e/) |

> **Current release/state:** `PHYSICAL_PENDING` — digital pipelines + synthetic smoke exist; absolute spatial accuracy on hardware is pending.

Ecosystem portal: [gunnchos-research-portal](https://github.com/gunnchOS3k/gunnchos-research-portal) · Product charter: [gunnchOS3k_PRODUCT_CHARTER.md](https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/blob/main/program/charter/gunnchOS3k_PRODUCT_CHARTER.md)

## What is this?

Schemas, probes, firmware/research paths, and opt-in telemetry for Edge I/O Rings and related measurement nodes.

## Why does it exist?

Embodied input and honest network/experience metrics need a dedicated measurement layer with consent and claim discipline.

## Where does it fit?

Product Charter **layer 7** (Ring sensing/measurement). Consumed by `gunnchos-device-os` Ring/input paths.

## What is real today?

- Schema-validated synthetic / smoke telemetry (`make smoke` / `make e2e`)
- Privacy helpers and 7GC/Lab export contracts
- Firmware and gate1 digital fabrication *research* artifacts as documented in-tree

## What is simulated / modelled?

- Synthetic measurement batches and emulator-style probes
- Spatial accuracy labelled SIMULATED until physical calibration

## What is physical / external pending?

- Physical Ring spatial registration / anti-spoof / comfort (E6)
- Representative field campaigns (not citywide claims)
- Any carrier or certification claim — **not authorized**

## Try / inspect in 5 minutes

```bash
pip install -r requirements.txt
make test
make smoke   # synthetic — not field evidence
```
See [docs/EXTERNAL_RESEARCHER_QUICKSTART.md](docs/EXTERNAL_RESEARCHER_QUICKSTART.md).

## Architecture

Python package + `firmware/` + `fixtures/` + privacy/consent gates + export contracts toward Lab / research twin consumers.

## Repo map

| Path | Role |
|---|---|
| `clients/` / package code | Measurement clients |
| `firmware/` | Ring/node firmware research |
| `fixtures/` | Valid synthetic batches |
| `physical_evidence/` | Physical capture staging |
| `docs/` | Protocols and claim honesty |

## Interfaces

JSON telemetry contracts consumed by device-os / field-kit pipelines. Opt-in only; no PII by default.

## Tests

```bash
make lint test contract-test
```

## Evidence

[reproducibility/](reproducibility/) and `results/` smoke records. Field-validated campaigns are separate.

## Known gaps

Physical spatial accuracy, HIL Ring-to-app proof, non-synthetic community measurement sets.

## Beginner path

Think of a **consenting fitness tracker for network/input experience** — not a spy tool.

## Intern path

Run `make smoke`, open one fixture, and map fields to the claim boundary.

## Expert path

Tighten firmware/Lab contracts; keep `physical_spatial_pending` honest.

## Contribution path

Schemas, tests, privacy, firmware harnesses. No unauthorized RF collection.

## Current release / state

**PHYSICAL_PENDING**. Research prototype — not certified consumer hardware.

## Claim boundary

No commercial 6G · no certification · IMU alone ≠ absolute spatial registration · Cursor DRAFT-only.

---

## Retained detail (post–Cycle 3A front door)

Full historical README: [docs/history/README_PRE_WP012.md](docs/history/README_PRE_WP012.md).

Useful retained entrypoints: [docs/START_HERE.md](docs/START_HERE.md) · [docs/WHAT_IS_REAL_TODAY.md](docs/WHAT_IS_REAL_TODAY.md) · [docs/END_TO_END_READINESS.md](docs/END_TO_END_READINESS.md).
