/* SPDX-License-Identifier: Apache-2.0 */
#include "dw3000.h"

int dw3000_init(dw3000_dev_t *dev, ring_spi_bus_t *bus, uint8_t cs_id, bool populated) {
  uint8_t tx[2] = {DW3000_REG_DEV_ID, 0};
  uint8_t rx[2] = {0, 0};
  if (!dev) return RING_BUS_ERR_INVAL;
  dev->bus = bus;
  dev->cs_id = cs_id;
  dev->populated = populated;
  dev->ready = false;
  if (!populated) {
    /* DNP: compile-clean no-op success (optional module absent). */
    return RING_BUS_OK;
  }
  if (!bus || !bus->xfer) return RING_BUS_ERR_INVAL;
  if (bus->xfer(bus, cs_id, tx, rx, 2) != RING_BUS_OK) return RING_BUS_ERR_IO;
  if (rx[1] != DW3000_DEV_ID_EXPECT) return RING_BUS_ERR_NO_DEV;
  dev->ready = true;
  return RING_BUS_OK;
}

int dw3000_range(dw3000_dev_t *dev, dw3000_range_t *out) {
  uint8_t tx[5] = {0x01, 0, 0, 0, 0};
  uint8_t rx[5] = {0};
  if (!dev || !out) return RING_BUS_ERR_INVAL;
  if (!dev->populated) {
    out->range_mm = 0;
    out->ranging_ok = false;
    return RING_BUS_OK; /* DNP path */
  }
  if (!dev->ready) return RING_BUS_ERR_INVAL;
  if (dev->bus->xfer(dev->bus, dev->cs_id, tx, rx, 5) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  out->range_mm = ((uint32_t)rx[1]) | ((uint32_t)rx[2] << 8) |
                  ((uint32_t)rx[3] << 16) | ((uint32_t)rx[4] << 24);
  out->ranging_ok = true;
  return RING_BUS_OK;
}
