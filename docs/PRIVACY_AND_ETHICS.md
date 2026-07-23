# Privacy and Ethics — Edge-IO Measurement Node

This document governs **exploratory field measurements** for the gunnchos **phone-first field console**. It applies to Wi-Fi/network QoE logging and any discussion of **receive-only SDR observation**. It does **not** authorize covert monitoring or non-consensual data collection.

---

## Core commitments

1. **No private third-party traffic payload collection.** We do not capture packet payloads, HTTP bodies, DNS queries, or application content from other users.
2. **No packet payload inspection.** Metrics are limited to latency, loss, jitter, RSSI, throughput summaries, and device status.
3. **Opt-in only.** Logging and export require explicit participant consent (`consent_flag=true`).
4. **No minors without guardian/program approval.** School or youth programs require institutional review and parental consent pathways.
5. **Aggregated reporting.** Public reports use campaign-level statistics; individual traces are access-controlled.
6. **Retention and deletion.** Raw logs default to short retention; toy mode deletes after export (`delete_after_export_toy`). Production pilots will publish a campaign-specific schedule.

---

## Public Wi-Fi measurement boundaries

- Measure **your device's** experience, not other clients' traffic.
- Do not associate measurements with identifiable individuals in public spaces.
- Use **location labels** (waypoints) rather than publishing precise GPS in open datasets.
- Post signage or verbal notice when running structured pilot sessions.

---

## Receive-only RF observation (SDR)

If SDR tooling is discussed elsewhere in the portfolio:

- **Receive-only** spectrum observation for education/research labeling.
- **No unauthorized transmission.**
- No decoding of private communications content.
- Follow local regulations (e.g., FCC Part 15 receive-only practice for US researchers).

---

## Implementation hooks

- Schema validation: `src/edge_io_node/telemetry_schema.py`
- Export filtering: `src/edge_io_node/privacy.py`
- Synthetic demo: `python3 -m edge_io_node.demo --toy`

---

## What this does not claim

- Carrier-grade monitoring
- Citywide representative sampling
- Certified test equipment compliance
- IRB approval (obtain before human-subjects field campaigns)

Cross-reference: umbrella `docs/PRIVACY_AND_ETHICS.md` in `gunnchos-7gc-ai-ran-field-kit`.
