/* SPDX-License-Identifier: Apache-2.0 */
/*
 * Qorvo/Decawave DW3000-class (DWM3001C) — optional UWB path.
 * Zephyr has DW1000 only; this is a compile-clean DNP/populated driver.
 */
#ifndef RING_DW3000_H
#define RING_DW3000_H

#include "../bus/ring_bus.h"

#define DW3000_CS_ID_DEFAULT   0
#define DW3000_REG_DEV_ID      0x00
#define DW3000_REG_SYS_CFG     0x10
#define DW3000_REG_SYS_STATUS  0x11
#define DW3000_REG_RANGE       0x01
#define DW3000_REG_SOFT_RST    0x7F
#define DW3000_DEV_ID_EXPECT   0xDE
#define DW3000_SYS_CFG_RXEN    0x01
#define DW3000_SOFT_RST_VAL    0x01
#define DW3000_STATUS_OK       0x01

typedef struct {
  uint32_t range_mm;
  bool ranging_ok;
  uint8_t sys_status;
} dw3000_range_t;

typedef struct {
  uint8_t device_id;
  uint8_t sys_cfg;
  uint32_t range_ok;
  uint32_t range_fail;
  uint32_t recoveries;
  bool ready;
  bool populated;
} dw3000_diag_t;

typedef struct {
  ring_spi_bus_t *bus;
  uint8_t cs_id;
  bool ready;
  bool populated;
  uint8_t sys_cfg;
  uint32_t range_ok;
  uint32_t range_fail;
  uint32_t recoveries;
} dw3000_dev_t;

int dw3000_init(dw3000_dev_t *dev, ring_spi_bus_t *bus, uint8_t cs_id, bool populated);
int dw3000_configure(dw3000_dev_t *dev, uint8_t sys_cfg);
int dw3000_soft_reset(dw3000_dev_t *dev);
int dw3000_recover(dw3000_dev_t *dev);
int dw3000_range(dw3000_dev_t *dev, dw3000_range_t *out);
int dw3000_diagnostics(dw3000_dev_t *dev, dw3000_diag_t *out);

#endif
