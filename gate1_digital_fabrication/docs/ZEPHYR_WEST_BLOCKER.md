# Zephyr / west digital probe

Generated: `2026-08-07T23:40:26Z`

## Tokens
```text
RING_ZEPHYR_WEST_BUILD_SOFT_SKIP
RING_PHYSICAL_BOOT_PENDING
```

## Isolated west
- west present: `True`
- west version: `West version: v1.5.0`
- isolated venv: `.toolchain/west-venv`
- global pip pollution: `False`

## Blockers (exact)
- ZEPHYR_BASE unset/missing — full zephyrproject west init/update not performed (multi-GB modules; not installed in this digital pass)
- ZEPHYR_SDK_INSTALL_DIR unset/missing — full Zephyr SDK ~1.1GB macos-aarch64 archive download blocked/deferred (policy + disk headroom); freestanding clang ARM path remains authoritative

## Not claimed
- `RING_ZEPHYR_WEST_BUILD_PASS` (requires successful `west build`)
- Physical flash / boot

## Authoritative digital path
Freestanding ARM clang + MCUboot DEVELOPMENT pipeline.
