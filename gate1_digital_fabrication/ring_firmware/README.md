# Edge I/O Ring — Development Firmware

**Label:** development firmware (`0.1.0-dev`)  
**Tokens (digital):** `RING_MCU_TARGET_FIRMWARE_BUILD_PASS` · `RING_MCUBOOT_DEV_PIPELINE_PASS` · `RING_PHYSICAL_BOOT_PENDING`  
**Zephyr west:** `RING_ZEPHYR_WEST_BUILD_PASS` — see `docs/ZEPHYR_WEST_BUILD_PASS.md` (Wave A real west build).  
**Freeze:** PHYSICAL_EXECUTION_FREEZE ACTIVE — not flashed to physical hardware in this pass.

## Build

```bash
cd gate1_digital_fabrication/ring_firmware
make clean && make all
```

Produces:
- Debug + release-development ARM artifacts: `{elf,bin,hex,map}` + SHA256
- Host tests + `host_sim` + `native_sim` (BLE stub + anti-replay)
- MCUboot DEVELOPMENT pipeline: signed slot0 / slot1 update / revert / factory-test + negatives
- Static analysis + Zephyr-shaped board/DT under `boards/` + `dts/`
- Isolated west venv under `.toolchain/west-venv` (gitignored; no global pip)

Requires: `clang` (ARM target), `python3.11`, `pytest`.  
Full Zephyr SDK soft-skips when absent (`make zephyr-soft` / `zephyr-west-probe`).

## Isolated west (optional)

```bash
make zephyr-west-setup   # venv + west only
make zephyr-west-probe   # writes ZEPHYR_WEST_PROBE.json + blocker doc
```
