# Ring Firmware Status

Generated: `2026-08-09T17:15:31Z`

```text
RING_MCU_TARGET_FIRMWARE_BUILD_PASS
RING_MCUBOOT_DEV_PIPELINE_PASS
RING_ZEPHYR_WEST_BUILD_SOFT_SKIP
RING_FULL_FIRMWARE_DIGITAL_PASS
RING_ZEPHYR_NATIVE_PATH_DIGITAL_PASS
RING_PHYSICAL_BOOT_PENDING
```

Label: **development firmware** (portable drivers + fusion app + host/native_sim).
MCUboot: DEVELOPMENT sign/update/revert/factory-test/anti-replay.

## Continuation VII
- Driver depth: configure/recover/diagnostics for BMI270, IQS7222A, SE050, npm1300, DW3000
- Zephyr-native path: DEVICE_DT_GET, I2C/SPI bus, BLE, settings, PM, MCUboot Kconfig
- E2E digital input scenario token: RING_END_TO_END_DIGITAL_INPUT_PASS (repo tests)

## Continuation VI (retained)
- Real device tree nodes (no *_STUB labels)
- Portable drivers + fusion application + build matrix + MCUboot DEV

## Not claimed
- Physical ring flash / boot
- Production MCUboot keys
- Full NXP Plug&Trust middleware (lite identity/auth path only)
- Physical accuracy / latency

## Build
```bash
cd gate1_digital_fabrication/ring_firmware
make clean && make all
```
