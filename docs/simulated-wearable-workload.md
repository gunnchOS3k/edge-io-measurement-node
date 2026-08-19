# Simulated Wearable Workload

## Overview

All wearable workload evaluation in this repository uses simulation and emulation. **No body-worn human data is collected without ethics approval.** This simulation path is sufficient for evaluating service-continuity methods under ultra-low-latency constraints.

## Simulation Components

### Synthetic Sensor Streams

Generated sensor data with configurable parameters:

- **IMU (accelerometer/gyroscope)**: Synthetic motion profiles including walking, running, stationary, and transition patterns
- **Environmental sensors**: Temperature, humidity, and pressure traces with realistic drift and noise
- **Proximity/touch**: Simulated interaction events with configurable frequency and duration
- **Noise injection**: Gaussian noise, quantization noise, and sensor-specific noise models applied to clean signals

### Replayed IMU Traces

Pre-recorded inertial measurement data used for reproducible evaluation:

- Sourced from public motion capture datasets (with appropriate licensing)
- Converted to target sensor format (sample rate, resolution, coordinate frame)
- Annotated with ground-truth event labels for benchmark comparison
- Covers a range of motion types and intensities

### Emulated Haptic Feedback Timing

Modeled actuator response for evaluating end-to-end latency:

- **Linear resonant actuator (LRA)** model: rise time, braking time, resonant frequency
- **Eccentric rotating mass (ERM)** model: spin-up and spin-down characteristics
- **Piezoelectric** model: near-instantaneous response with amplitude constraints
- Feedback timing validated against published actuator datasheets

### QEMU Firmware Simulation

Full microcontroller firmware execution in emulation:

- ARM Cortex-M target emulation via QEMU
- Cycle-approximate timing for interrupt handling and DMA transfers
- Peripheral models for ADC, SPI, I2C, UART, and timer subsystems
- BLE/UWB radio modeled as latency-injecting message queues

## Evaluation Scenarios

| Scenario | Sensor Load | Feedback Type | Latency Target |
|---|---|---|---|
| Haptic response benchmark | Single IMU @ 200 Hz | LRA haptic | < 10 ms |
| Safety alert benchmark | Multi-sensor @ 100 Hz | Audio + haptic | < 20 ms |
| Continuous monitoring | Environmental @ 10 Hz | Display update | < 50 ms |
| Burst workload | IMU @ 200 Hz + proximity @ 100 Hz | Multi-modal | < 10 ms primary |
| Energy-constrained | IMU @ 50 Hz (duty-cycled) | Haptic (infrequent) | < 10 ms when active |

## What This Simulation Validates

- **Latency budgets**: Whether the processing pipeline meets event-to-feedback targets
- **Energy feasibility**: Whether the workload fits within coin-cell or small LiPo energy budgets
- **Processing pipeline correctness**: Whether sensor events are classified and routed correctly
- **Link behavior**: Whether BLE/UWB transmission fits within the latency budget
- **Thermal modeling**: Whether sustained sensing stays within safe thermal limits

## What This Simulation Does Not Validate

- Real-world radio interference and environmental noise
- Actual human perception of haptic feedback quality
- Physical device comfort, fit, or ergonomics
- Battery chemistry behavior under thermal stress
- Electromagnetic compatibility in real deployment environments

## Ethics Compliance

This simulation-based approach ensures:

- No human participant data is required for workload evaluation
- All sensor traces are synthetic or from properly licensed public datasets
- Research results are reproducible without access to physical hardware or human subjects
- The simulation path can be extended with real data after ethics approval is obtained
