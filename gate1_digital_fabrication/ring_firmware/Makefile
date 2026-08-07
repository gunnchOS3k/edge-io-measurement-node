# Edge I/O Ring development firmware
CLANG ?= clang
PY ?= python3.11
CFLAGS_HOST = -O0 -g -Wall -Wextra -Iinclude -DRING_DEVELOPMENT=1
CFLAGS_ARM = -target armv7em-none-unknown-eabi -ffreestanding -nostdlib -Os -Wall -Iinclude -DRING_FREESTANDING=1 -DRING_DEVELOPMENT=1

.PHONY: all test host sha artifacts host-sim clean

all: artifacts test host-sim

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

artifacts: build/ring_fw_host.elf
	@mkdir -p build/out
	cp build/ring_fw_host.elf build/out/ring_firmware_dev_host.elf
	$(CLANG) $(CFLAGS_ARM) -fno-builtin -c src/startup_arm.c -o build/startup_arm.o
	$(CLANG) $(CFLAGS_ARM) -fno-builtin -c src/ring_fw_freestanding.c -o build/ring_fw_arm.o
	$(PY) scripts/pack_arm_elf.py build/startup_arm.o build/ring_fw_arm.o build/out
	@echo 0.1.0-dev > build/out/VERSION.txt
	@echo label: development >> build/out/VERSION.txt
	@echo board: edge_io_ring_evt0 >> build/out/VERSION.txt
	cd build/out && shasum -a 256 ring_firmware_dev.elf ring_firmware_dev.bin ring_firmware_dev.hex ring_firmware_dev.map VERSION.txt ring_firmware_dev_host.elf > SHA256SUMS
	@echo ARTIFACTS_OK

test: build/test_ring_fw.elf build/ring_fw_host.elf
	./build/test_ring_fw.elf
	./build/ring_fw_host.elf
	$(PY) -m pytest -q tests/test_protocol_host.py

host: build/ring_fw_host.elf
	./build/ring_fw_host.elf

host-sim:
	$(PY) host_sim/ring_host_sim.py --self-check

sha: artifacts

clean:
	rm -rf build
