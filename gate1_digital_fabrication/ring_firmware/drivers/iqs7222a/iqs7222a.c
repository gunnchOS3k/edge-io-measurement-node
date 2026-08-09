/* SPDX-License-Identifier: Apache-2.0 */
#include "iqs7222a.h"

int iqs7222a_soft_reset(iqs7222a_dev_t *dev) {
  uint8_t ctrl = IQS7222A_SYS_CTRL_RESET;
  if (!dev || !dev->bus) return RING_BUS_ERR_INVAL;
  dev->ready = false;
  return ring_i2c_reg_write(dev->bus, dev->addr7, IQS7222A_REG_SYS_CONTROL, &ctrl, 1);
}

int iqs7222a_configure(iqs7222a_dev_t *dev, uint8_t sys_control) {
  if (!dev || !dev->bus) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_write(dev->bus, dev->addr7, IQS7222A_REG_SYS_CONTROL, &sys_control, 1)
      != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  dev->sys_control = sys_control;
  return RING_BUS_OK;
}

int iqs7222a_init(iqs7222a_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7) {
  uint8_t prod = 0;
  if (!dev || !bus) return RING_BUS_ERR_INVAL;
  dev->bus = bus;
  dev->addr7 = addr7 ? addr7 : IQS7222A_I2C_ADDR_DEFAULT;
  dev->ready = false;
  dev->read_ok = 0;
  dev->read_fail = 0;
  dev->recoveries = 0;
  if (ring_i2c_reg_read(bus, dev->addr7, IQS7222A_REG_PROD_NUM, &prod, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (prod != IQS7222A_PROD_NUM_EXPECT) return RING_BUS_ERR_NO_DEV;
  if (iqs7222a_configure(dev, IQS7222A_SYS_CTRL_ATI) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  dev->ready = true;
  return RING_BUS_OK;
}

int iqs7222a_recover(iqs7222a_dev_t *dev) {
  int rc;
  if (!dev) return RING_BUS_ERR_INVAL;
  (void)iqs7222a_soft_reset(dev);
  rc = iqs7222a_init(dev, dev->bus, dev->addr7);
  if (rc == RING_BUS_OK) dev->recoveries++;
  return rc;
}

int iqs7222a_read_state(iqs7222a_dev_t *dev, iqs7222a_state_t *out) {
  uint8_t st = 0, flags = 0, lsb = 0, msb = 0;
  if (!dev || !out || !dev->ready) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, IQS7222A_REG_SYS_STATUS, &st, 1) != RING_BUS_OK) {
    dev->read_fail++;
    return RING_BUS_ERR_IO;
  }
  if (ring_i2c_reg_read(dev->bus, dev->addr7, IQS7222A_REG_TOUCH_FLAGS, &flags, 1)
      != RING_BUS_OK) {
    dev->read_fail++;
    return RING_BUS_ERR_IO;
  }
  if (ring_i2c_reg_read(dev->bus, dev->addr7, IQS7222A_REG_CH_COUNT_LSB, &lsb, 1)
      != RING_BUS_OK) {
    dev->read_fail++;
    return RING_BUS_ERR_IO;
  }
  if (ring_i2c_reg_read(dev->bus, dev->addr7, IQS7222A_REG_CH_COUNT_MSB, &msb, 1)
      != RING_BUS_OK) {
    dev->read_fail++;
    return RING_BUS_ERR_IO;
  }
  out->sys_status = st;
  out->touch_flags = flags;
  out->proximity = (flags & 0x01) != 0;
  out->touch = (flags & 0x02) != 0;
  out->channel_count = (uint16_t)(((uint16_t)msb << 8) | lsb);
  /* Normalize against datasheet-ish full-scale stand-in 4095 */
  out->strength = out->channel_count > 4095 ? 1.0f : ((float)out->channel_count / 4095.0f);
  if ((st & 0x80) != 0) {
    /* device-reported fault → recover once */
    (void)iqs7222a_recover(dev);
  }
  dev->read_ok++;
  return RING_BUS_OK;
}

int iqs7222a_diagnostics(iqs7222a_dev_t *dev, iqs7222a_diag_t *out) {
  uint8_t prod = 0, ver = 0;
  if (!dev || !out) return RING_BUS_ERR_INVAL;
  out->ready = dev->ready;
  out->sys_control = dev->sys_control;
  out->read_ok = dev->read_ok;
  out->read_fail = dev->read_fail;
  out->recoveries = dev->recoveries;
  out->prod = 0;
  out->version = 0;
  if (!dev->bus) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, IQS7222A_REG_PROD_NUM, &prod, 1) == RING_BUS_OK)
    out->prod = prod;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, IQS7222A_REG_VERSION, &ver, 1) == RING_BUS_OK)
    out->version = ver;
  return RING_BUS_OK;
}
