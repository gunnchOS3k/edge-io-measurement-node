# Ring BOM ↔ schematic ↔ firmware parity — Continuation V

Updated: 2026-08-08T20:15:00Z  
Branch: `cursor/full-product-continuation-v-ring-firmware-parity`  
Base: `fc617e831916362e77aa157d77d458e935dc4cfa`  
Hardware counterpart: `gunnchos-hardware-industrial-design` `device_designs/edge_io_rings/docs/BOM_SCH_FW_PARITY.md`

PHYSICAL_EXECUTION_FREEZE ACTIVE — not flashed.

## What changed here
1. Extended `dts/pinout.json` with IQS7222A, SE050, npm1300, optional UWB/mag/hub stubs matching hardware BOM.
2. Extended board DT with reserved CAP_INT / SE_IRQ GPIOs (stubs).
3. Did **not** expand Zephyr `zephyr_app/src/main.c` beyond smoke — still printk loop.

## Remaining gaps
| Item | Status |
|---|---|
| Real IQS7222A / SE050 / npm1300 Zephyr drivers | NOT STARTED |
| Confirm I2C addresses vs EVT1 schematic straps | PENDING hardware review |
| DWM3001C SPI CS pin | TBD on schematic |
| `RING_PHYSICAL_BOOT` | PENDING (freeze) |

## Tokens
- Claimed: `RING_FW_PINOUT_PARITY_STUBS_CONTINUATION_V`
- Not claimed: full fusion firmware, physical boot, sensor bring-up
