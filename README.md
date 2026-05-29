# Edge-IO Measurement Node

Reframes **Edge-IO** and gunnchOS devices as **low-cost edge measurement endpoints** for 6G education, AI inference, and network quality measurement.

> **Research prototype** — not certified consumer hardware. All collection **opt-in** and **privacy-preserving**.

## Measures (planned)

Latency, jitter, packet loss, RSSI, device temperature, CPU/GPU utilization, offline AI timing, interaction traces (aggregated).

## 7GC spine

Exports to [7gc-digital-twin](https://github.com/gunnchOS3k/7gc-digital-twin) via `export_to_7gc.py` contract.

```bash
pip install -r requirements.txt && pytest -q
```
