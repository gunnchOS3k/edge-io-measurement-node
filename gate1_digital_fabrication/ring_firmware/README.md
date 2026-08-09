# Edge I/O Ring — Development Firmware (Continuation VII)

**Label:** development firmware (`0.1.0-dev`)  
**Tokens (digital):** `RING_FULL_FIRMWARE_DIGITAL_PASS` · `RING_ZEPHYR_NATIVE_PATH_DIGITAL_PASS` · `RING_END_TO_END_DIGITAL_INPUT_PASS` · `RING_PHYSICAL_BOOT_PENDING`  
**Freeze:** PHYSICAL_EXECUTION_FREEZE ACTIVE — not flashed to physical hardware.

## Build

```bash
cd gate1_digital_fabrication/ring_firmware
make clean && make all
```

Produces:
- Host fusion app + deepened portable drivers (BMI270, IQS7222A, SE050, npm1300, DW3000, BMM350)
- Zephyr-native path (`DEVICE_DT_GET`, BLE, settings, PM) with `CONFIG_RING_USE_FAKE_BUS` for DK
- Build matrix: base / uwb / mag / debug / release-dev
- Host tests + `host_sim` failure scenarios + `native_sim` + driver-depth proof
- MCUboot DEVELOPMENT signed artifacts
- Truthful Zephyr-shaped DT + custom bindings (no `*_STUB` nodes)
- Optional: `make zephyr-west-build` when Zephyr SDK present

Repo E2E (from repo root):

```bash
PYTHONPATH=src pytest -q tests/test_ring_e2e_digital.py
```

Requires: `clang`, `python3.11`, `pytest`.
