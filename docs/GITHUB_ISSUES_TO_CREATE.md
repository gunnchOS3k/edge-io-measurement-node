# GitHub Issues to Create

## Issue 1: Define formal sensing workload benchmark specification

**Labels**: documentation, research

Formalize the wearable sensing benchmark with specific parameters: sensor sample rates, event-to-feedback latency targets, energy budgets, and BLE/UWB link requirements. Include acceptance criteria for each metric and define the evaluation methodology using simulation tools.

---

## Issue 2: Implement latency measurement framework in simulation

**Labels**: enhancement, simulation

Build an end-to-end latency measurement framework within the QEMU firmware simulation environment. The framework should timestamp sensor events at generation, trace processing stages, and capture actuation command timing to validate latency budgets (< 10 ms haptic, < 20 ms safety, < 50 ms informational).

---

## Issue 3: Create synthetic sensor trace library

**Labels**: enhancement, simulation

Develop a library of synthetic sensor traces (IMU, environmental, proximity) with configurable noise profiles, sample rates, and motion patterns. Include replayed IMU traces from public datasets with ground-truth annotations for benchmark reproducibility.

---

## Issue 4: Document privacy boundary and ethics review process

**Labels**: documentation, ethics

Formalize the privacy-and-body-data-boundary policy into an enforceable checklist. Define the process for obtaining ethics review approval before any human participant data collection. Ensure all simulation-based evaluation paths are clearly documented as the default.

---

## Issue 5: Establish energy model and thermal simulation for sensing workloads

**Labels**: enhancement, simulation

Create a power consumption model for the Edge IO sensing workload covering sensor acquisition, processing, radio transmission, and actuation. Include thermal modeling for body-worn operation. Validate that target workloads fit within coin-cell and small LiPo energy budgets.
