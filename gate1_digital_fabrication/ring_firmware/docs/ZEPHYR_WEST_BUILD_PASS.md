# RING_ZEPHYR_WEST_BUILD_PASS

Generated: Wave A full-product toolchain pass.

```text
RING_ZEPHYR_WEST_BUILD_PASS
RING_PHYSICAL_BOOT_PENDING
```

## Environment
- Zephyr: v3.7.1 at `~/zephyr-workspace/zephyr`
- west: v1.5.0 (isolated `.toolchain/west-venv`)
- SDK: zephyr-sdk-0.16.8 (`arm-zephyr-eabi`) at `~/zephyr-workspace/zephyr-sdk-0.16.8`
- CMake: 3.31.10 via venv (Homebrew CMake 4.4.1 is incompatible with Zephyr 3.7.1)
- Board: `nrf52840dk/nrf52840` (nRF52840 ring MCU target)
- App: `gate1_digital_fabrication/ring_firmware/zephyr_app`

## Build
```bash
export ZEPHYR_BASE=$HOME/zephyr-workspace/zephyr
export ZEPHYR_SDK_INSTALL_DIR=$HOME/zephyr-workspace/zephyr-sdk-0.16.8
export ZEPHYR_TOOLCHAIN_VARIANT=zephyr
export PATH=$PWD/.toolchain/west-venv/bin:$PATH
west build -b nrf52840dk/nrf52840 -d build/zephyr_west zephyr_app
```

## Artifacts
- `build/zephyr_west/zephyr/zephyr.elf`
- `build/out/zephyr_west/ring_zephyr_nrf52840.{elf,bin,hex}`
- `build/out/zephyr_west/SHA256SUMS`
- `docs/WEST_BUILD_LOG.txt`

## Not claimed
- Physical flash / boot (`RING_PHYSICAL_BOOT_PENDING`)
- PRODUCTION keys
