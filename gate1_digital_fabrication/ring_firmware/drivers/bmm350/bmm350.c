/* SPDX-License-Identifier: Apache-2.0 */
#include "bmm350.h"
int bmm350_init(bmm350_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7, bool enabled) {
  uint8_t id = 0;
  if (!dev) return RING_BUS_ERR_INVAL;
  dev->bus = bus; dev->addr7 = addr7 ? addr7 : BMM350_I2C_ADDR_DEFAULT;
  dev->enabled = enabled; dev->ready = false;
  if (!enabled) return RING_BUS_OK;
  if (!bus) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_read(bus, dev->addr7, BMM350_REG_CHIP_ID, &id, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (id != BMM350_CHIP_ID_VALUE) return RING_BUS_ERR_NO_DEV;
  dev->ready = true; return RING_BUS_OK;
}
int bmm350_sample(bmm350_dev_t *dev, bmm350_sample_t *out) {
  uint8_t raw[6] = {0};
  if (!dev || !out) return RING_BUS_ERR_INVAL;
  if (!dev->enabled) { out->mx = out->my = out->mz = 0; return RING_BUS_OK; }
  if (!dev->ready) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, 0x04, raw, 6) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  out->mx = (float)((int16_t)(raw[0] | (raw[1] << 8))) / 16.0f;
  out->my = (float)((int16_t)(raw[2] | (raw[3] << 8))) / 16.0f;
  out->mz = (float)((int16_t)(raw[4] | (raw[5] << 8))) / 16.0f;
  return RING_BUS_OK;
}
