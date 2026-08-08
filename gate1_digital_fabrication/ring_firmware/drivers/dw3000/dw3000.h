/* SPDX-License-Identifier: Apache-2.0 */
/*
 * Qorvo/Decawave DW3000-class (DWM3001C) — optional UWB path.
 * Zephyr has DW1000 only; this is a compile-clean DNP/populated driver.
 * CS GPIO: P0.20 EVT1 candidate — see EDA parity note (schematic CS was TBD).
 */
#ifndef RING_DW3000_H
#define RING_DW3000_H

#include "../bus/ring_bus.h"

#define DW3000_CS_ID_DEFAULT   0
#define DW3000_REG_DEV_ID      0x00
#define DW3000_DEV_ID_EXPECT   0xDE /* digital device-id marker for DW3xxx class */

typedef struct {
  uint32_t range_mm;
  bool ranging_ok;
} dw3000_range_t;

typedef struct {
  ring_spi_bus_t *bus;
  uint8_t cs_id;
  bool ready;
  bool populated; /* false = DNP compile-clean path */
} dw3000_dev_t;

int dw3000_init(dw3000_dev_t *dev, ring_spi_bus_t *bus, uint8_t cs_id, bool populated);
int dw3000_range(dw3000_dev_t *dev, dw3000_range_t *out);

#endif
