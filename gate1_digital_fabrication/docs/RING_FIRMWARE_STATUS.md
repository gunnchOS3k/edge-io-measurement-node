# Ring Firmware — Digital Fabrication Status

Generated: 2026-08-07T22:25:26Z
Label: **development firmware**
Tokens: `RING_DIGITAL_FABRICATION_PACKAGE_COMPLETE` · `RING_PHYSICAL_PROTOTYPE_PENDING`

## Compile
```bash
cd gate1_digital_fabrication/ring_firmware
make clean && make artifacts && make test && make host-sim
```

## Artifacts
`build/out/ring_firmware_dev.{elf,bin,hex,map}` · host ELF · `SHA256SUMS` · `VERSION.txt`
