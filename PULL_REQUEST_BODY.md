# Add PhD application readiness documentation

## Summary

- Define the wearable sensing benchmark with event-to-feedback latency targets (< 10 ms haptic, < 20 ms safety, < 50 ms informational), energy budgets, and BLE/UWB link requirements
- Document the event-to-feedback latency breakdown across sensor acquisition, processing, transmission, and actuation stages
- Establish the privacy and body data boundary policy: body-area data classified as sensitive, ethics review required, data minimization mandatory, local processing preferred
- Define the simulation-based evaluation plan: synthetic sensor streams, replayed IMU traces, emulated haptic timing, QEMU firmware simulation

## What This Does NOT Claim

- No deployed wearable devices
- No human participant testing or data collection
- No validated body-area network performance from physical hardware
- No measured (non-simulated) latency or energy figures

## Files Added

- `docs/PHD_APPLICATION_READINESS.md` — Overall readiness status and definition of done
- `docs/wearable-sensing-benchmark.md` — Sensing benchmark specification
- `docs/event-to-feedback-latency.md` — Latency definition and stage budgets
- `docs/privacy-and-body-data-boundary.md` — Privacy policy for body-area data
- `docs/simulated-wearable-workload.md` — Simulation-based evaluation plan
- `docs/GITHUB_ISSUES_TO_CREATE.md` — Follow-up issues for implementation work
