/*
 * Edge I/O Ring EVT0 — Zephyr-shaped board definition for nRF52840.
 * Pinout mirrors gate1 schematic netlist (digital fab). No physical boot claim.
 */
#ifndef BOARD_EDGE_IO_RING_H
#define BOARD_EDGE_IO_RING_H

#define BOARD_NAME "edge_io_ring_evt0"
#define BOARD_MCU  "nRF52840"
#define BOARD_SOC  "nrf52840"

/* GPIO map from schematic/netlist.json */
#define RING_PIN_I2C_SDA     26  /* P0.26 */
#define RING_PIN_I2C_SCL     27  /* P0.27 */
#define RING_PIN_IMU_INT     11  /* P0.11 */
#define RING_PIN_CHG_STATUS   2  /* P0.02 */

#define RING_I2C_ADDR_BMI270   0x68
#define RING_I2C_ADDR_DRV2605L 0x5A

#endif /* BOARD_EDGE_IO_RING_H */
