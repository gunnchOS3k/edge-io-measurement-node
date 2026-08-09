/* SPDX-License-Identifier: Apache-2.0 */
#include "npm1300.h"

int npm1300_soft_reset(npm1300_dev_t *dev) {
  uint8_t rst = NPM1300_RESET_SOFT;
  if (!dev || !dev->bus) return RING_BUS_ERR_INVAL;
  dev->ready = false;
  return ring_i2c_reg_write(dev->bus, dev->addr7, NPM1300_REG_RESET, &rst, 1);
}

int npm1300_configure(npm1300_dev_t *dev, uint8_t adc_config) {
  if (!dev || !dev->bus) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_write(dev->bus, dev->addr7, NPM1300_REG_ADC_CONFIG, &adc_config, 1)
      != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  dev->adc_config = adc_config;
  return RING_BUS_OK;
}

int npm1300_init(npm1300_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7) {
  uint8_t mark = 0;
  if (!dev || !bus) return RING_BUS_ERR_INVAL;
  dev->bus = bus;
  dev->addr7 = addr7 ? addr7 : NPM1300_I2C_ADDR_DEFAULT;
  dev->ready = false;
  dev->read_ok = 0;
  dev->read_fail = 0;
  dev->recoveries = 0;
  if (ring_i2c_reg_read(bus, dev->addr7, NPM1300_MARK_REG, &mark, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (mark != NPM1300_MARK_VALUE) return RING_BUS_ERR_NO_DEV;
  if (npm1300_configure(dev, NPM1300_ADC_CFG_ENABLE) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  dev->ready = true;
  return RING_BUS_OK;
}

int npm1300_recover(npm1300_dev_t *dev) {
  int rc;
  if (!dev) return RING_BUS_ERR_INVAL;
  (void)npm1300_soft_reset(dev);
  rc = npm1300_init(dev, dev->bus, dev->addr7);
  if (rc == RING_BUS_OK) dev->recoveries++;
  return rc;
}

int npm1300_read_status(npm1300_dev_t *dev, npm1300_status_t *out) {
  uint8_t msb = 0, lsb = 0, vbus = 0, chg_err = 0;
  if (!dev || !out || !dev->ready) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, NPM1300_REG_ADC_VBAT_MSB, &msb, 1)
      != RING_BUS_OK) {
    dev->read_fail++;
    return RING_BUS_ERR_IO;
  }
  if (ring_i2c_reg_read(dev->bus, dev->addr7, NPM1300_REG_ADC_VBAT_LSB, &lsb, 1)
      != RING_BUS_OK) {
    dev->read_fail++;
    return RING_BUS_ERR_IO;
  }
  if (ring_i2c_reg_read(dev->bus, dev->addr7, NPM1300_REG_VBUSIN_STATUS, &vbus, 1)
      != RING_BUS_OK) {
    dev->read_fail++;
    return RING_BUS_ERR_IO;
  }
  if (ring_i2c_reg_read(dev->bus, dev->addr7, NPM1300_REG_BCHG_ERR, &chg_err, 1)
      != RING_BUS_OK) {
    dev->read_fail++;
    (void)npm1300_recover(dev);
    return RING_BUS_ERR_IO;
  }
  out->vbat_mv = (uint16_t)(((uint16_t)msb << 8) | lsb);
  if (out->vbat_mv >= 4100) out->soc_pct = 100;
  else if (out->vbat_mv <= 3300) out->soc_pct = 0;
  else out->soc_pct = (uint8_t)((out->vbat_mv - 3300) * 100 / 800);
  out->vbus_present = (vbus & 0x01) != 0;
  out->charging = (vbus & 0x02) != 0;
  out->charger_err = chg_err;
  if (chg_err != 0) (void)npm1300_recover(dev);
  dev->read_ok++;
  return RING_BUS_OK;
}

int npm1300_diagnostics(npm1300_dev_t *dev, npm1300_diag_t *out) {
  uint8_t mark = 0;
  if (!dev || !out) return RING_BUS_ERR_INVAL;
  out->ready = dev->ready;
  out->adc_config = dev->adc_config;
  out->read_ok = dev->read_ok;
  out->read_fail = dev->read_fail;
  out->recoveries = dev->recoveries;
  out->mark = 0;
  if (!dev->bus) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, NPM1300_MARK_REG, &mark, 1) == RING_BUS_OK)
    out->mark = mark;
  return RING_BUS_OK;
}
