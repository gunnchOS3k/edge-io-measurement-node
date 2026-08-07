# Edge I/O Ring — Zephyr-shaped nRF52840 freestanding firmware
# Primary path: clang -target armv7em-none-eabi (reproducible without full Zephyr SDK)
# Optional: west build when ZEPHYR_BASE is set (soft-skip otherwise)
# Tokens: RING_MCU_TARGET_FIRMWARE_BUILD_PASS · RING_PHYSICAL_BOOT_PENDING
# PHYSICAL_EXECUTION_FREEZE: no physical boot claim.

CLANG ?= clang
PY ?= python3.11
CFLAGS_HOST = -O0 -g -Wall -Wextra -Iinclude -Iboards/arm/edge_io_ring -DRING_DEVELOPMENT=1
CFLAGS_ARM_COMMON = -target armv7em-none-eabi -ffreestanding -nostdlib -Wall -Iinclude -Iboards/arm/edge_io_ring -DRING_FREESTANDING=1 -DRING_DEVELOPMENT=1 -fno-builtin
CFLAGS_ARM_DEBUG = $(CFLAGS_ARM_COMMON) -O0 -g -DRING_BUILD_DEBUG=1
CFLAGS_ARM_RELDEV = $(CFLAGS_ARM_COMMON) -Os -DNDEBUG -DRING_BUILD_RELEASE_DEVELOPMENT=1

.PHONY: all test host sha artifacts host-sim native-sim mcuboot clean zephyr-soft debug release-development status size-report zephyr-board-check

all: artifacts test host-sim native-sim mcuboot size-report zephyr-board-check zephyr-soft status

build/ring_fw_host.o: src/ring_fw.c include/ring_fw.h
	@mkdir -p build
	$(CLANG) $(CFLAGS_HOST) -c src/ring_fw.c -o $@

build/main_host.o: src/main.c include/ring_fw.h
	@mkdir -p build
	$(CLANG) $(CFLAGS_HOST) -c src/main.c -o $@

build/ring_fw_host.elf: build/ring_fw_host.o build/main_host.o
	$(CLANG) $(CFLAGS_HOST) $^ -o $@

build/test_ring_fw.elf: tests/test_ring_fw.c build/ring_fw_host.o
	$(CLANG) $(CFLAGS_HOST) tests/test_ring_fw.c build/ring_fw_host.o -o $@

debug: build/out/.stamp_debug

release-development: build/out/.stamp_reldev

build/out/.stamp_debug:
	@mkdir -p build/out build/debug
	$(CLANG) $(CFLAGS_ARM_DEBUG) -c src/startup_arm.c -o build/debug/startup_arm.o
	$(CLANG) $(CFLAGS_ARM_DEBUG) -c src/ring_fw_freestanding.c -o build/debug/ring_fw_arm.o
	$(PY) scripts/pack_arm_elf.py build/debug/startup_arm.o build/debug/ring_fw_arm.o --out build/out --name ring_firmware_debug
	@touch $@

build/out/.stamp_reldev:
	@mkdir -p build/out build/reldev
	$(CLANG) $(CFLAGS_ARM_RELDEV) -c src/startup_arm.c -o build/reldev/startup_arm.o
	$(CLANG) $(CFLAGS_ARM_RELDEV) -c src/ring_fw_freestanding.c -o build/reldev/ring_fw_arm.o
	$(PY) scripts/pack_arm_elf.py build/reldev/startup_arm.o build/reldev/ring_fw_arm.o --out build/out --name ring_firmware_release_development
	@touch $@

artifacts: build/ring_fw_host.elf debug release-development
	@mkdir -p build/out
	cp build/ring_fw_host.elf build/out/ring_firmware_dev_host.elf
	cp build/out/ring_firmware_release_development.elf build/out/ring_firmware_dev.elf
	cp build/out/ring_firmware_release_development.bin build/out/ring_firmware_dev.bin
	cp build/out/ring_firmware_release_development.hex build/out/ring_firmware_dev.hex
	cp build/out/ring_firmware_release_development.map build/out/ring_firmware_dev.map
	@echo 0.1.0-dev > build/out/VERSION.txt
	@echo label: development >> build/out/VERSION.txt
	@echo board: edge_io_ring_evt0 >> build/out/VERSION.txt
	@echo mcu: nRF52840 >> build/out/VERSION.txt
	@echo physical_boot: PENDING >> build/out/VERSION.txt
	$(PY) scripts/write_sha256sums.py
	@echo ARTIFACTS_OK

test: build/test_ring_fw.elf build/ring_fw_host.elf
	./build/test_ring_fw.elf
	./build/ring_fw_host.elf
	$(PY) -m pytest -q tests/test_protocol_host.py tests/test_pinout_board.py tests/test_mcuboot_fixtures.py

host: build/ring_fw_host.elf
	./build/ring_fw_host.elf

host-sim:
	$(PY) host_sim/ring_host_sim.py --self-check

native-sim:
	$(PY) native_sim/native_sim_boot.py --self-check

mcuboot: artifacts
	$(PY) scripts/mcuboot_dev_sign.py
	$(PY) scripts/write_sha256sums.py

zephyr-soft:
	@if [ -n "$${ZEPHYR_BASE:-}" ] && command -v west >/dev/null 2>&1; then \
	  echo "ZEPHYR_WEST_PRESENT — soft path available (not required for Gate1 closeout)"; \
	else \
	  echo "ZEPHYR_SDK_ABSENT soft-skip; freestanding ARM path is authoritative"; \
	fi

zephyr-board-check:
	@test -f boards/arm/edge_io_ring/board.yml
	@test -f boards/edge_io_ring/edge_io_ring.dts -o -f dts/edge_io_ring.dts
	@echo ZEPHYR_BOARD_DEFINITION_PRESENT

size-report: artifacts
	@echo "=== size report (ARM image) ==="
	@wc -c build/out/ring_firmware_dev.bin build/out/ring_firmware_dev.elf || true
	@echo "=== map head ==="
	@head -20 build/out/ring_firmware_dev.map || true

status:
	@$(PY) scripts/write_firmware_status.py

sha: artifacts

clean:
	rm -rf build
