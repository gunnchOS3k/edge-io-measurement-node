# Edge I/O Ring — Development Firmware

**Label:** development firmware (`0.1.0-dev`)  
**Tokens:** `RING_MCU_TARGET_FIRMWARE_BUILD_PASS` · `RING_PHYSICAL_BOOT_PENDING`  
**Freeze:** PHYSICAL_EXECUTION_FREEZE ACTIVE — not flashed to physical hardware in this pass.

## Build

```bash
cd gate1_digital_fabrication/ring_firmware
make clean && make all
```

Produces:
- Debug + release-development ARM artifacts: `{elf,bin,hex,map}` + SHA256
- Host tests + `host_sim` + `native_sim`
- MCUboot DEVELOPMENT signing + tampered negative fixtures
- Zephyr-shaped board/DT under `boards/arm/edge_io_ring` + `dts/`

Requires: `clang` (ARM target), `python3`, `pytest`, `openssl` (optional).  
Full Zephyr SDK/`west` soft-skips when absent (`make zephyr-soft`).
