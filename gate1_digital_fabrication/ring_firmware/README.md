# Edge I/O Ring — Development Firmware

**Label:** development firmware (`0.1.0-dev`)  
**Tokens:** `RING_DIGITAL_FABRICATION_PACKAGE_COMPLETE` · `RING_PHYSICAL_PROTOTYPE_PENDING`  
**Freeze:** PHYSICAL_EXECUTION_FREEZE ACTIVE — not flashed to physical hardware in this pass.

## Build

```bash
cd gate1_digital_fabrication/ring_firmware
make clean && make artifacts
make test
make host-sim
```

Artifacts: `build/out/ring_firmware_dev.{elf,bin,hex,map}` + `SHA256SUMS` + `VERSION.txt`

Requires: `clang` (ARM target), `python3.11`, `pytest`.
