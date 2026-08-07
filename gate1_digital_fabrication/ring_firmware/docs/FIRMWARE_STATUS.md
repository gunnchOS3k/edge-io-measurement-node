# Ring Firmware Status

Updated: `2026-08-07T22:21:57Z`

Label: **development firmware** (host-compiled reference + unit tests).

Target MCU: nRF52840 (physical flash pending `REQUIRES_LOCAL_HARDWARE`).

Build:

```bash
cd gate1_digital_fabrication/ring_firmware && make test && make sha && make host
```

Produces ELF/BIN, SHA256, version metadata. Not a claim of on-device validation.
