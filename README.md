# Edge-IO Measurement Node
## End-to-End Research Artifact

| Item | Detail |
|------|--------|
| **Runs today** | Research prototype with smoke test (synthetic, non-evidence) |
| **Demo** | `make e2e (smoke test only — not readiness proof) (smoke test only — not readiness proof)` |
| **Data** | Synthetic only — no private IQ or PII |
| **Extend** | See [EXTERNAL_RESEARCHER_QUICKSTART.md](docs/EXTERNAL_RESEARCHER_QUICKSTART.md) |
| **Limits** | Not operational 6G; not Oulu affiliation; not carrier-grade |
| **Readiness** | [END_TO_END_READINESS.md](docs/END_TO_END_READINESS.md) |
| **Proof** | [E2E_RUN_RECORD.md](reproducibility/E2E_RUN_RECORD.md) |
| **Artifacts** | [results/e2e/](results/e2e/) |

Reframes **Edge-IO** and gunnchOS devices as **low-cost edge measurement endpoints** for 6G education, AI inference, and network quality measurement.

> **Research prototype** — not certified consumer hardware. All collection **opt-in** and **privacy-preserving**.

## Measures (planned)

Latency, jitter, packet loss, RSSI, device temperature, CPU/GPU utilization, offline AI timing, interaction traces (aggregated).

## 7GC spine

Exports to [7gc-digital-twin](https://github.com/gunnchOS3k/7gc-digital-twin) via `export_to_7gc.py` contract.

```bash
pip install -r requirements.txt && pytest -q
```
