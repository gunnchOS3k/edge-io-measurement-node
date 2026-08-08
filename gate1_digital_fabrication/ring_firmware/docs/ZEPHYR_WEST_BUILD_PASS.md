# RING_ZEPHYR_WEST_BUILD_PASS

Generated: Continuation VI full fusion zephyr_app.

```text
RING_ZEPHYR_WEST_BUILD_PASS
RING_FULL_FIRMWARE_DIGITAL_PASS
RING_PHYSICAL_BOOT_PENDING
```

## Environment
- Zephyr: v3.7.1
- west: v1.5.0 (isolated `.toolchain/west-venv`)
- SDK: zephyr-sdk-0.16.8
- Board: `nrf52840dk/nrf52840`
- App: `zephyr_app` full fusion (portable drivers + fake bus on DK)

## Build
```bash
export ZEPHYR_BASE=$HOME/zephyr-workspace/zephyr
export ZEPHYR_SDK_INSTALL_DIR=$HOME/zephyr-workspace/zephyr-sdk-0.16.8
export ZEPHYR_TOOLCHAIN_VARIANT=zephyr
export PATH=$PWD/.toolchain/west-venv/bin:$PATH
make zephyr-west-build
```

## Not claimed
- Physical flash / boot (`RING_PHYSICAL_BOOT_PENDING`)
- Production keys
