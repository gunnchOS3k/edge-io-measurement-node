/* SPDX-License-Identifier: Apache-2.0 */
#include "iqs7222a.h"

int iqs7222a_init(iqs7222a_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7) {
  uint8_t prod = 0;
  if (!dev || !bus) return RING_BUS_ERR_INVAL;
  dev->bus = bus;
  dev->addr7 = addr7 ? addr7 : IQS7222A_I2C_ADDR_DEFAULT;
  dev->ready = false;
  if (ring_i2c_reg_read(bus, dev->addr7, IQS7222A_REG_PROD_NUM, &prod, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (prod != IQS7222A_PROD_NUM_EXPECT) return RING_BUS_ERR_NO_DEV;
  dev->ready = true;
  return RING_BUS_OK;
}

int iqs7222a_read_state(iqs7222a_dev_t *dev, iqs7222a_state_t *out) {
  uint8_t st = 0, flags = 0;
  if (!dev || !out || !dev->ready) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, IQS7222A_REG_SYS_STATUS, &st, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, IQS7222A_REG_TOUCH_FLAGS, &flags, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  out->sys_status = st;
  out->touch_flags = flags;
  out->proximity = (flags & 0x01) != 0;
  out->touch = (flags & 0x02) != 0;
  return RING_BUS_OK;
}
