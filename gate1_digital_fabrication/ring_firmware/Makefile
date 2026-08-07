# Edge I/O Ring development firmware — DIGITAL / NONPHYSICAL
# Label: development firmware (not production signed image)
CLANG ?= clang
TARGET = armv7em-none-unknown-eabi
CFLAGS = -target $(TARGET) -ffreestanding -nostdlib -Os -Wall -Wextra -Iinclude -DRING_DEVELOPMENT=1
SRCS = $(wildcard src/*.c)
OBJS = $(patsubst src/%.c,build/%.o,$(SRCS))
BUILD = build
OUT = build/out
PY = python3.11

.PHONY: all clean test host-sim artifacts

all: artifacts

build/%.o: src/%.c
	@mkdir -p build
	$(CLANG) $(CFLAGS) -c $< -o $@

artifacts: $(OBJS)
	@mkdir -p $(OUT)
	$(PY) scripts/pack_arm_elf.py $(OBJS) $(OUT)
	@echo "DEVELOPMENT FIRMWARE ARTIFACTS in $(OUT)"

# Hosted unit-test compile (native) for logic modules without Reset loop
HOST_SRCS = src/boot.c src/identity.c src/ble_pairing.c src/auth_anti_replay.c \
	src/sensors.c src/fusion_filter.c src/gesture.c src/calibration.c \
	src/battery.c src/low_power.c src/haptics.c src/dfu.c src/diagnostics.c \
	src/telemetry.c src/factory_test.c
HOST_OBJS = $(patsubst src/%.c,build/host_%.o,$(notdir $(HOST_SRCS)))

build/host_%.o: src/%.c
	@mkdir -p build
	$(CLANG) -c -O0 -g -Iinclude -DRING_DEVELOPMENT=1 $< -o $@

build/host_test_runner: tests/test_runner.c $(HOST_OBJS)
	$(CLANG) -O0 -g -Iinclude -DRING_DEVELOPMENT=1 tests/test_runner.c $(HOST_OBJS) -o $@

test: build/host_test_runner
	./build/host_test_runner
	$(PY) -m pytest -q tests/test_protocol_host.py host_simulator

host-sim:
	$(PY) host_simulator/ring_host_sim.py --self-check

clean:
	rm -rf build
