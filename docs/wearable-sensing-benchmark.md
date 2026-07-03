# Wearable Sensing Benchmark

## Purpose

This document defines the wearable sensing benchmark for the Edge IO measurement node. The Edge IO is **not an accessory** — it is the low-latency sensing and haptic workload benchmark device in the Device Quartet, representing the most demanding class of edge sensing constraints.

## Event-to-Feedback Latency Targets

| Feedback Type | Target Latency | Rationale |
|---|---|---|
| Haptic feedback | < 10 ms | Perceptual threshold for tactile responsiveness |
| Safety alert | < 20 ms | Time-critical protective response |
| Informational update | < 50 ms | User-perceptible but non-critical |

These targets define the end-to-end latency budget from sensor event detection to user-perceptible feedback. See [event-to-feedback-latency.md](event-to-feedback-latency.md) for the full breakdown.

## Sensing Sample Rates

| Sensor Class | Minimum Sample Rate | Notes |
|---|---|---|
| IMU (accelerometer/gyroscope) | 200 Hz | Motion detection, gesture recognition |
| Environmental (temperature, humidity) | 1–10 Hz | Ambient monitoring |
| Proximity / touch | 100 Hz | Interaction detection |
| Biometric-like (if ethics-approved) | 50–200 Hz | Heart rate, skin conductance |

## Energy Budgets

| Power Source | Capacity | Target Operational Duration |
|---|---|---|
| Coin cell (CR2032) | ~225 mAh @ 3V | 8+ hours at low duty cycle |
| Small LiPo (100–300 mAh) | 100–300 mAh @ 3.7V | 4–8 hours continuous sensing |

### Energy Constraints

- Peak current draw must remain within coin-cell discharge limits (~15 mA burst)
- Duty cycling required for continuous operation
- Radio (BLE/UWB) dominates power budget — minimize transmit time
- Processing must complete within inter-sample intervals to avoid buffering overhead

## BLE/UWB Link Requirements

| Parameter | BLE | UWB |
|---|---|---|
| Range | 10–30 m typical | 10–50 m typical |
| Throughput | 1–2 Mbps (BLE 5) | 6.8–27.2 Mbps |
| Latency contribution | 2–5 ms per event | < 1 ms per event |
| Use case | Sensor data streaming, control | Precision ranging, low-latency events |

## Device Quartet Context

The Edge IO represents the most constrained device in the quartet:

- **Smallest form factor** — body-worn or near-body
- **Tightest energy budget** — coin-cell or small LiPo
- **Strictest latency requirements** — sub-10ms haptic feedback
- **Most sensitive data** — body-area sensing requires privacy-first design

This benchmark defines the floor for service-continuity research: if the system can maintain quality of experience under Edge IO constraints, it can handle the less demanding workloads of the other quartet devices.

## Evaluation Method

All benchmarks are evaluated using:

- Synthetic sensor streams
- Replayed IMU traces
- Emulated haptic feedback timing
- QEMU firmware simulation

No body-worn human data is collected without ethics approval.
