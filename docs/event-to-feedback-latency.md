# Event-to-Feedback Latency

## Definition

Event-to-feedback latency is the total time from **sensor event detection** to **user-perceptible feedback** (haptic vibration, HUD update, safety alert). This is the primary performance metric for the Edge IO measurement node.

## Latency Targets

| Feedback Class | Target | Justification |
|---|---|---|
| Haptic feedback | < 10 ms | Below human tactile perception threshold; enables responsive interaction |
| Safety alert | < 20 ms | Fast enough for protective response initiation |
| Informational display | < 50 ms | Perceived as instantaneous for non-critical updates |

## Latency Breakdown

The end-to-end latency is composed of four sequential stages:

```
Sensor Acquisition → Processing → Transmission → Actuation
```

### Stage Budgets

| Stage | Haptic (< 10 ms) | Safety (< 20 ms) | Informational (< 50 ms) |
|---|---|---|---|
| Sensor acquisition | 1–2 ms | 2–3 ms | 5 ms |
| Processing | 2–3 ms | 3–5 ms | 10 ms |
| Transmission | 2–3 ms | 5–7 ms | 15 ms |
| Actuation | 2–3 ms | 5–7 ms | 10–15 ms |
| **Total budget** | **< 10 ms** | **< 20 ms** | **< 50 ms** |

### Stage Descriptions

**Sensor Acquisition**
Time from physical event occurrence to digital sample availability. Includes ADC conversion, DMA transfer, and interrupt latency.

**Processing**
Time to classify, filter, or decide on the sensor event. Includes signal processing, threshold detection, and decision logic.

**Transmission**
Time to deliver the processed result to the actuator or display subsystem. May be on-chip (negligible) or over BLE/UWB (2–7 ms).

**Actuation**
Time from command receipt to user-perceptible output. Includes motor spin-up for haptics, display refresh for HUD, or audio generation for alerts.

## Measurement Method

All latency measurements use **end-to-end timestamps in simulation or emulation**:

1. **Timestamp injection**: Synthetic sensor events carry a generation timestamp
2. **Pipeline tracing**: Each processing stage appends its entry/exit timestamps
3. **Feedback capture**: Actuation command timestamp is recorded
4. **Latency calculation**: Feedback timestamp minus event generation timestamp

### Measurement Environment

- **QEMU firmware simulation** for microcontroller timing
- **Synthetic sensor streams** with known timing characteristics
- **Emulated radio links** with configurable latency profiles
- **Modeled actuator response** based on datasheet specifications

## Jitter

Latency jitter (variation in event-to-feedback time) is tracked alongside mean latency:

- **Haptic path**: Jitter must be < 2 ms to avoid perceptible inconsistency
- **Safety path**: Jitter must be < 5 ms to maintain reliable response time
- **Informational path**: Jitter up to 10 ms is acceptable

## Limitations

- All latency figures are simulated or modeled — not measured on physical hardware
- Radio latency models are based on published BLE/UWB specifications, not field measurements
- Actuator response times are based on datasheet values, not measured performance
- Real-world performance may differ due to interference, thermal effects, and hardware variation
