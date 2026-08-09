# Edge I/O Ring — full digital firmware (Continuation VI)
# Primary: clang host + freestanding ARM + host_sim. Optional: Zephyr west.
# Token: RING_FULL_FIRMWARE_DIGITAL_PASS when app+drivers+builds pass (physical boot pending).
# PHYSICAL_EXECUTION_FREEZE: no physical boot claim.

CLANG ?= clang
PY ?= python3.11
INCLUDES = -Iinclude -Iboards/arm/edge_io_ring -I. -Idrivers -Iapp
CFLAGS_HOST = -O0 -g -Wall -Wextra $(INCLUDES) -DRING_DEVELOPMENT=1
CFLAGS_ARM_COMMON = -target armv7em-none-eabi -ffreestanding -nostdlib -Wall -Iinclude -Iboards/arm/edge_io_ring -DRING_FREESTANDING=1 -DRING_DEVELOPMENT=1 -fno-builtin
CFLAGS_ARM_DEBUG = $(CFLAGS_ARM_COMMON) -O0 -g -DRING_BUILD_DEBUG=1
CFLAGS_ARM_RELDEV = $(CFLAGS_ARM_COMMON) -Os -DNDEBUG -DRING_BUILD_RELEASE_DEVELOPMENT=1

DRIVER_SRCS = \
	drivers/bus/ring_bus_fake.c \
	drivers/bmi270/bmi270.c \
	drivers/iqs7222a/iqs7222a.c \
	drivers/se050/se050.c \
	drivers/npm1300/npm1300.c \
	drivers/dw3000/dw3000.c \
	drivers/bmm350/bmm350.c \
	app/ring_app.c

DRIVER_HOST_OBJS = $(patsubst %.c,build/%.o,$(DRIVER_SRCS))

.PHONY: all test host sha artifacts host-sim native-sim mcuboot mcuboot-sign clean \
	zephyr-soft zephyr-west-setup zephyr-west-probe zephyr-west-build \
	debug release-development status size-report zephyr-board-check static-analysis \
	matrix matrix-base matrix-uwb matrix-mag matrix-debug matrix-release-dev

all: artifacts test host-sim native-sim mcuboot matrix static-analysis size-report zephyr-board-check zephyr-west-setup zephyr-west-probe zephyr-soft status

build/%.o: %.c
	@mkdir -p $(dir $@)
	$(CLANG) $(CFLAGS_HOST) -c $< -o $@

build/ring_fw_host.o: src/ring_fw.c include/ring_fw.h
	@mkdir -p build
	$(CLANG) $(CFLAGS_HOST) -c src/ring_fw.c -o $@

build/main_host.o: src/main.c include/ring_fw.h app/ring_app.h
	@mkdir -p build
	$(CLANG) $(CFLAGS_HOST) -c src/main.c -o $@

build/ring_fw_host.elf: build/ring_fw_host.o build/main_host.o $(DRIVER_HOST_OBJS)
	$(CLANG) $(CFLAGS_HOST) $^ -o $@

build/test_ring_fw.elf: tests/test_ring_fw.c build/ring_fw_host.o
	$(CLANG) $(CFLAGS_HOST) tests/test_ring_fw.c build/ring_fw_host.o -o $@

build/test_ring_app.elf: tests/test_ring_app.c $(DRIVER_HOST_OBJS)
	$(CLANG) $(CFLAGS_HOST) tests/test_ring_app.c $(DRIVER_HOST_OBJS) -o $@

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
	@echo digital: RING_FULL_FIRMWARE_DIGITAL_CANDIDATE >> build/out/VERSION.txt
	$(PY) scripts/write_sha256sums.py
	@echo ARTIFACTS_OK

test: build/test_ring_fw.elf build/test_ring_app.elf build/ring_fw_host.elf
	./build/test_ring_fw.elf
	./build/test_ring_app.elf
	./build/ring_fw_host.elf
	$(PY) -m pytest -q tests/test_protocol_host.py tests/test_pinout_board.py tests/test_mcuboot_fixtures.py tests/test_mcuboot_pipeline.py tests/test_ble_stub.py tests/test_full_firmware_digital.py tests/test_continuation_vii.py

host: build/ring_fw_host.elf
	./build/ring_fw_host.elf

host-sim:
	$(PY) host_sim/ring_host_sim.py --self-check

native-sim:
	$(PY) native_sim/native_sim_boot.py --self-check

# Build matrix: base / uwb / mag / debug / release-dev host apps
matrix: matrix-base matrix-uwb matrix-mag matrix-debug matrix-release-dev
	@echo MATRIX_OK > build/out/BUILD_MATRIX_OK.txt
	@echo MATRIX_OK

matrix-base:
	@mkdir -p build/matrix/base
	$(CLANG) $(CFLAGS_HOST) -DRING_FEATURE_UWB=0 -DRING_FEATURE_MAG=0 -c src/main.c -o build/matrix/base/main.o
	$(CLANG) $(CFLAGS_HOST) -DRING_FEATURE_UWB=0 -DRING_FEATURE_MAG=0 $(DRIVER_SRCS) build/matrix/base/main.o src/ring_fw.c -o build/matrix/base/ring_base.elf
	./build/matrix/base/ring_base.elf > build/matrix/base/run.log
	@cp build/matrix/base/ring_base.elf build/out/ring_firmware_matrix_base.elf

matrix-uwb:
	@mkdir -p build/matrix/uwb
	$(CLANG) $(CFLAGS_HOST) -DRING_FEATURE_UWB=1 -DRING_FEATURE_MAG=0 -c src/main.c -o build/matrix/uwb/main.o
	$(CLANG) $(CFLAGS_HOST) -DRING_FEATURE_UWB=1 -DRING_FEATURE_MAG=0 $(DRIVER_SRCS) build/matrix/uwb/main.o src/ring_fw.c -o build/matrix/uwb/ring_uwb.elf
	./build/matrix/uwb/ring_uwb.elf > build/matrix/uwb/run.log
	@cp build/matrix/uwb/ring_uwb.elf build/out/ring_firmware_matrix_uwb.elf

matrix-mag:
	@mkdir -p build/matrix/mag
	$(CLANG) $(CFLAGS_HOST) -DRING_FEATURE_UWB=0 -DRING_FEATURE_MAG=1 -c src/main.c -o build/matrix/mag/main.o
	$(CLANG) $(CFLAGS_HOST) -DRING_FEATURE_UWB=0 -DRING_FEATURE_MAG=1 $(DRIVER_SRCS) build/matrix/mag/main.o src/ring_fw.c -o build/matrix/mag/ring_mag.elf
	./build/matrix/mag/ring_mag.elf > build/matrix/mag/run.log
	@cp build/matrix/mag/ring_mag.elf build/out/ring_firmware_matrix_mag.elf

matrix-debug: debug
	@cp build/out/ring_firmware_debug.elf build/out/ring_firmware_matrix_debug.elf

matrix-release-dev: release-development
	@cp build/out/ring_firmware_release_development.elf build/out/ring_firmware_matrix_release_dev.elf

mcuboot: artifacts
	$(PY) scripts/mcuboot_dev_pipeline.py
	$(PY) scripts/write_sha256sums.py

mcuboot-sign: mcuboot

static-analysis:
	$(PY) scripts/static_analysis.py

zephyr-west-setup:
	@bash scripts/setup_zephyr_west_isolated.sh

zephyr-west-probe:
	@$(PY) scripts/zephyr_west_probe.py

zephyr-west-build: zephyr-west-setup
	@bash scripts/zephyr_west_build_full.sh

zephyr-soft: zephyr-west-probe
	@if [ -n "$${ZEPHYR_BASE:-}" ] && [ -n "$${ZEPHYR_SDK_INSTALL_DIR:-}" ] && command -v west >/dev/null 2>&1; then \
	  echo "ZEPHYR_WEST_ENV_PRESENT"; \
	elif [ -x .toolchain/west-venv/bin/west ]; then \
	  echo "WEST_ISOLATED_PRESENT; ZEPHYR_SDK may be absent — freestanding ARM path authoritative"; \
	else \
	  echo "ZEPHYR_SDK_ABSENT soft-skip; freestanding ARM path is authoritative"; \
	fi

zephyr-board-check:
	@test -f boards/arm/edge_io_ring/board.yml
	@test -f boards/edge_io_ring/edge_io_ring.dts -o -f dts/edge_io_ring.dts
	@test -f dts/pinout.json
	@grep -q 'bmi270@68' dts/edge_io_ring.dts
	@grep -q 'iqs7222a@44' dts/edge_io_ring.dts
	@grep -q 'se050@48' dts/edge_io_ring.dts
	@grep -q 'npm1300@6b' dts/edge_io_ring.dts
	@! grep -E 'label = ".*_STUB' dts/edge_io_ring.dts
	@echo ZEPHYR_BOARD_DEFINITION_PRESENT

size-report: artifacts
	@echo "=== size report (ARM image) ==="
	@wc -c build/out/ring_firmware_dev.bin build/out/ring_firmware_dev.elf || true
	@echo "=== map head ==="
	@head -20 build/out/ring_firmware_dev.map || true

status:
	@$(PY) scripts/write_firmware_status.py
	@$(PY) scripts/write_sha256sums.py

sha: artifacts

clean:
	rm -rf build
