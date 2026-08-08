# Ring Firmware Status

Generated: `2026-08-08T21:01:39Z`

```text
RING_MCU_TARGET_FIRMWARE_BUILD_PASS
RING_MCUBOOT_DEV_PIPELINE_PASS
RING_ZEPHYR_WEST_BUILD_PASS
RING_FULL_FIRMWARE_DIGITAL_PASS
RING_PHYSICAL_BOOT_PENDING
```

Label: **development firmware** (portable drivers + fusion app + host/native_sim).
MCUboot: DEVELOPMENT sign/update/revert/factory-test/anti-replay.

## Continuation VI
- Real device tree nodes (no *_STUB labels)
- Portable drivers: BMI270, IQS7222A, SE050, npm1300, DW3000(DNP), BMM350(opt)
- Fusion application: boot diag, sample, auth packet, BLE, cal, DFU, health
- Build matrix: base / uwb / mag / debug / release-dev + MCUboot DEV

## Not claimed
- Physical ring flash / boot
- Production MCUboot keys
- Full NXP Plug&Trust middleware (lite identity/auth path only)

## Build
```bash
cd gate1_digital_fabrication/ring_firmware
make clean && make all
```
