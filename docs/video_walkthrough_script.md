# Video Walkthrough — Edge IO privacy-preserving telemetry

## Opening (30s)
This repo is a **research prototype** for community-scale 6G research. Not operational deployment.

## Code tour
Open: `src/edge_io_node/telemetry_schema.py`, `src/edge_io_node/privacy.py`

Explain modules: telemetry_schema, privacy, demo

## Diagram tour
Show `docs/diagrams/code_path_main_demo.mmd` and `sequence_main_demo.mmd`.

## Demo
```bash
make e2e
```
Show: `results/e2e/sanitized_telemetry.json, privacy_report.md` — **synthetic toy data only**.

## Paper
Title in `paper/draft.md`. Toy results in `paper/preliminary_toy_results.md`.

## Closing
Complete for supervisor demo; field validation is future work.
