# Ring FULL firmware digital implementation — Continuation VI

Updated: 2026-08-08  
Branch: `cursor/full-product-continuation-vi-ring-firmware`  
Base: `4507c8fc9efc07a9f2debeef89f5f60f5ae97e5c` (#33)

PHYSICAL_EXECUTION_FREEZE ACTIVE — not flashed.

## Upstream / vendor drivers
| Device | Upstream | License posture | Ring path |
|---|---|---|---|
| BMI270 | Zephyr `bosch,bmi270` | Apache-2.0 | Portable driver aligned to Zephyr register map |
| npm1300 | Zephyr `nordic,npm1300` MFD/charger | Apache-2.0 | Portable driver + DT node `nordic,npm1300` |
| IQS7222A | None in Zephyr | Custom Apache-2.0 | Portable driver (datasheet defaults) |
| SE050 | NXP Plug&Trust MW (not vendored) | Lite custom | Identity/ATR + challenge path |
| DW3000 | Zephyr has DW1000 only | Custom Apache-2.0 | DNP compile-clean + populated SPI path |
| BMM350 | Optional | Custom | Optional matrix variant |

## Device tree
- Replaced all `*_STUB` labels with final nodes.
- UWB CS: **P0.20 EVT1_CANDIDATE** — schematic CS was TBD; cross-repo EDA must lock (see `dts/pinout.json` `eda_parity_notes`).

## Application
Replaces Zephyr printk smoke loop with fusion app:
boot diagnostics → sensor init → sample → timestamp → fusion frame → capacitive → SE identity/auth → battery → BLE → authenticated event MAC → calibration → DFU state → health telemetry.

## Host simulation
`host_sim` fake buses prove: init failure, invalid sensor, replay, low battery, calibration, packet loss, reconnect, UWB populated.

## Build matrix
base · ring+UWB · optional magnetometer · debug · release-dev · MCUboot signed DEV (no production key).

## Tokens
- Earnable: `RING_FULL_FIRMWARE_DIGITAL_PASS`
- Remains: `RING_PHYSICAL_BOOT_PENDING`
