# PhD Application Readiness — Edge IO Measurement Node

## Role

Edge IO measurement node — phone-first field console for edge measurement, representing the **wearable/sensing device class** in the Device Quartet. This device targets ultra-low-latency sensing and haptic feedback workloads in body-area and near-body environments.

## Status: Concept-Complete

### Complete

- Measurement mode documentation
- Edge IO architecture
- Privacy-first design for body-area data

### Prototype-Pending

- Formal sensing workload benchmarks
- Latency measurement framework (event-to-feedback)

### Simulation-Only

- All sensing evaluations use synthetic or replayed traces
- No body-worn hardware has been deployed or tested on humans

### Ethics-Gated

- Any body-worn sensing on human participants
- Location tracking or geospatial sensing
- Collection of biometric-like signals

## Metrics

| Metric | Target | Measurement Method |
|---|---|---|
| Event-to-feedback latency (haptic) | < 10 ms | End-to-end timestamp in simulation/emulation |
| Event-to-feedback latency (safety) | < 20 ms | End-to-end timestamp in simulation/emulation |
| Jitter | Minimized | Statistical analysis of latency distribution |
| Dropped events | < 0.1% under nominal load | Event counter comparison |
| Energy per sensing cycle | Within coin-cell / small LiPo budget | Simulated power model |
| BLE/UWB link quality | Reliable under mobility | Link simulation metrics |
| Thermal limits | Within safe body-contact range | Thermal model in simulation |

## Evidence

- Architecture documentation in this repository
- Measurement mode specification
- Privacy-first design documents
- Synthetic sensor trace library (planned)

## Must Not Claim

- Deployed wearable devices
- Human participant testing or data collection
- Validated body-area network performance from physical hardware
- Measured (non-simulated) latency or energy figures

## Fallback Approaches

- **Sensor trace replay**: Pre-recorded or synthetic IMU/sensor streams
- **QEMU firmware simulation**: Emulated microcontroller execution
- **Timing emulation**: Modeled latency budgets with synthetic workloads

## Definition of Done

1. Sensing workload specification documented with target parameters
2. Latency budgets defined for haptic, safety, and informational feedback paths
3. Simulation plan exists covering all evaluation scenarios
4. Privacy boundary enforced — no human data without ethics approval
5. Benchmark methodology documented and reproducible in simulation
