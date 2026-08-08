/*
 * Edge I/O Ring EVT0 — board definition for nRF52840.
 * Continuation VI truthful pinout. No physical boot claim.
 */
#ifndef BOARD_EDGE_IO_RING_H
#define BOARD_EDGE_IO_RING_H

#define BOARD_NAME "edge_io_ring_evt0"
#define BOARD_MCU  "nRF52840"
#define BOARD_SOC  "nrf52840"

#define RING_PIN_I2C_SDA     26  /* P0.26 */
#define RING_PIN_I2C_SCL     27  /* P0.27 */
#define RING_PIN_IMU_INT     11  /* P0.11 */
#define RING_PIN_CHG_STATUS   2  /* P0.02 */
#define RING_PIN_CAP_INT     15  /* P0.15 IQS7222A */
#define RING_PIN_SE_IRQ      16  /* P0.16 SE050 */
#define RING_PIN_NPM_INT      3  /* P0.03 npm1300 */
#define RING_PIN_UWB_IRQ     17  /* P0.17 DWM3001C DNP */
#define RING_PIN_UWB_CS      20  /* P0.20 EVT1_CANDIDATE — EDA lock required */

#define RING_I2C_ADDR_BMI270   0x68
#define RING_I2C_ADDR_DRV2605L 0x5A
#define RING_I2C_ADDR_IQS7222A 0x44
#define RING_I2C_ADDR_SE050    0x48
#define RING_I2C_ADDR_NPM1300  0x6B
#define RING_I2C_ADDR_BMM350   0x14

#endif /* BOARD_EDGE_IO_RING_H */
