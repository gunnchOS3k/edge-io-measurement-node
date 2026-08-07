# Ring Firmware Status

Generated: `2026-08-07T23:40:26Z`

```text
RING_MCU_TARGET_FIRMWARE_BUILD_PASS
RING_MCUBOOT_DEV_PIPELINE_PASS
RING_ZEPHYR_WEST_BUILD_SOFT_SKIP
RING_PHYSICAL_BOOT_PENDING
```

Label: **development firmware** (freestanding ARM + host/native_sim).
MCUboot: DEVELOPMENT sign/update/revert/factory-test/anti-replay.

## Not claimed
- Physical ring flash / boot
- Production MCUboot keys
- `RING_ZEPHYR_WEST_BUILD_PASS` unless west build truly succeeded

## Zephyr / west
Isolated `.toolchain/west-venv` when present; full SDK soft-skip documented in
`docs/ZEPHYR_WEST_BLOCKER.md`.

## Build
```bash
cd gate1_digital_fabrication/ring_firmware
make clean && make all
```

## Artifacts
`build/out/ring_firmware_{debug,release_development}.{elf,bin,hex,map}`
`build/out/mcuboot_pipeline/` · `SHA256SUMS`
