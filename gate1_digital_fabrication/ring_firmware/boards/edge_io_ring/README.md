# edge_io_ring board

Zephyr-shaped board/device-tree for nRF52840 Edge I/O Ring EVT0.

- Pinout documented from schematic assumptions (LED P0.13, BTN P0.11, I2C0).
- Physical pin verification: `RING_PHYSICAL_BOOT_PENDING`.
- Primary digital target build today: clang `armv7em-none-eabi` freestanding artifacts + MCUboot DEVELOPMENT signing.
- Full `west build` requires Zephyr SDK (Tier-1/T2 when installed); absence must not fail fixture CI.
