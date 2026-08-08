# Edge I/O Ring — Development Firmware (Continuation VI)

**Label:** development firmware (`0.1.0-dev`)  
**Tokens (digital):** `RING_FULL_FIRMWARE_DIGITAL_PASS` · `RING_MCU_TARGET_FIRMWARE_BUILD_PASS` · `RING_MCUBOOT_DEV_PIPELINE_PASS` · `RING_PHYSICAL_BOOT_PENDING`  
**Freeze:** PHYSICAL_EXECUTION_FREEZE ACTIVE — not flashed to physical hardware.

## Build

```bash
cd gate1_digital_fabrication/ring_firmware
make clean && make all
```

Produces:
- Host fusion app + portable drivers (BMI270, IQS7222A, SE050, npm1300, DW3000, BMM350)
- Build matrix: base / uwb / mag / debug / release-dev
- Host tests + `host_sim` failure scenarios + `native_sim`
- MCUboot DEVELOPMENT signed artifacts
- Truthful Zephyr-shaped DT (no `*_STUB` nodes)
- Optional: `make zephyr-west-build` when Zephyr SDK present

Requires: `clang`, `python3.11`, `pytest`.
