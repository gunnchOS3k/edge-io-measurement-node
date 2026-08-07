# Ring Firmware Status

Generated: `2026-08-07T23:11:32Z`

```text
RING_MCU_TARGET_FIRMWARE_BUILD_PASS
RING_PHYSICAL_BOOT_PENDING
```

Label: **development firmware** (freestanding ARM + host/native_sim).
MCUboot: DEVELOPMENT signing only.

## Not claimed
- Physical ring flash / boot
- Production MCUboot keys

## Build
```bash
cd gate1_digital_fabrication/ring_firmware
make clean && make all
```

## Artifacts
`build/out/ring_firmware_{debug,release_development}.{elf,bin,hex,map}`
`build/out/ring_firmware_mcuboot_signed_dev.bin` · `SHA256SUMS`
