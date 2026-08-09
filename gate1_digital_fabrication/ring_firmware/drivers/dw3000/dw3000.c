/* SPDX-License-Identifier: Apache-2.0 */
#include "dw3000.h"

int dw3000_soft_reset(dw3000_dev_t *dev) {
  uint8_t tx[2] = {DW3000_REG_SOFT_RST, DW3000_SOFT_RST_VAL};
  uint8_t rx[2] = {0};
  if (!dev || !dev->populated || !dev->bus || !dev->bus->xfer) return RING_BUS_ERR_INVAL;
  dev->ready = false;
  return dev->bus->xfer(dev->bus, dev->cs_id, tx, rx, 2);
}

int dw3000_configure(dw3000_dev_t *dev, uint8_t sys_cfg) {
  uint8_t tx[2] = {DW3000_REG_SYS_CFG, sys_cfg};
  uint8_t rx[2] = {0};
  if (!dev || !dev->populated || !dev->bus || !dev->bus->xfer) return RING_BUS_ERR_INVAL;
  if (dev->bus->xfer(dev->bus, dev->cs_id, tx, rx, 2) != RING_BUS_OK) return RING_BUS_ERR_IO;
  dev->sys_cfg = sys_cfg;
  return RING_BUS_OK;
}

int dw3000_init(dw3000_dev_t *dev, ring_spi_bus_t *bus, uint8_t cs_id, bool populated) {
  uint8_t tx[2] = {DW3000_REG_DEV_ID, 0};
  uint8_t rx[2] = {0, 0};
  if (!dev) return RING_BUS_ERR_INVAL;
  dev->bus = bus;
  dev->cs_id = cs_id;
  dev->populated = populated;
  dev->ready = false;
  dev->range_ok = 0;
  dev->range_fail = 0;
  dev->recoveries = 0;
  dev->sys_cfg = 0;
  if (!populated) {
    /* DNP: compile-clean no-op success (optional module absent). */
    return RING_BUS_OK;
  }
  if (!bus || !bus->xfer) return RING_BUS_ERR_INVAL;
  if (bus->xfer(bus, cs_id, tx, rx, 2) != RING_BUS_OK) return RING_BUS_ERR_IO;
  if (rx[1] != DW3000_DEV_ID_EXPECT) return RING_BUS_ERR_NO_DEV;
  if (dw3000_configure(dev, DW3000_SYS_CFG_RXEN) != RING_BUS_OK) return RING_BUS_ERR_IO;
  dev->ready = true;
  return RING_BUS_OK;
}

int dw3000_recover(dw3000_dev_t *dev) {
  int rc;
  if (!dev || !dev->populated) return RING_BUS_ERR_INVAL;
  (void)dw3000_soft_reset(dev);
  rc = dw3000_init(dev, dev->bus, dev->cs_id, true);
  if (rc == RING_BUS_OK) dev->recoveries++;
  return rc;
}

int dw3000_range(dw3000_dev_t *dev, dw3000_range_t *out) {
  uint8_t stx[2] = {DW3000_REG_SYS_STATUS, 0};
  uint8_t srx[2] = {0};
  uint8_t tx[5] = {DW3000_REG_RANGE, 0, 0, 0, 0};
  uint8_t rx[5] = {0};
  if (!dev || !out) return RING_BUS_ERR_INVAL;
  if (!dev->populated) {
    out->range_mm = 0;
    out->ranging_ok = false;
    out->sys_status = 0;
    return RING_BUS_OK; /* DNP path */
  }
  if (!dev->ready) return RING_BUS_ERR_INVAL;
  if (dev->bus->xfer(dev->bus, dev->cs_id, stx, srx, 2) != RING_BUS_OK) {
    dev->range_fail++;
    return RING_BUS_ERR_IO;
  }
  out->sys_status = srx[1];
  if ((srx[1] & DW3000_STATUS_OK) == 0) {
    dev->range_fail++;
    (void)dw3000_recover(dev);
    out->ranging_ok = false;
    out->range_mm = 0;
    return RING_BUS_ERR_IO;
  }
  if (dev->bus->xfer(dev->bus, dev->cs_id, tx, rx, 5) != RING_BUS_OK) {
    dev->range_fail++;
    return RING_BUS_ERR_IO;
  }
  out->range_mm = ((uint32_t)rx[1]) | ((uint32_t)rx[2] << 8) |
                  ((uint32_t)rx[3] << 16) | ((uint32_t)rx[4] << 24);
  out->ranging_ok = true;
  dev->range_ok++;
  return RING_BUS_OK;
}

int dw3000_diagnostics(dw3000_dev_t *dev, dw3000_diag_t *out) {
  uint8_t tx[2] = {DW3000_REG_DEV_ID, 0};
  uint8_t rx[2] = {0};
  if (!dev || !out) return RING_BUS_ERR_INVAL;
  out->ready = dev->ready;
  out->populated = dev->populated;
  out->sys_cfg = dev->sys_cfg;
  out->range_ok = dev->range_ok;
  out->range_fail = dev->range_fail;
  out->recoveries = dev->recoveries;
  out->device_id = 0;
  if (!dev->populated || !dev->bus || !dev->bus->xfer) return RING_BUS_OK;
  if (dev->bus->xfer(dev->bus, dev->cs_id, tx, rx, 2) == RING_BUS_OK)
    out->device_id = rx[1];
  return RING_BUS_OK;
}
