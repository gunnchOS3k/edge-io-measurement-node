/* SPDX-License-Identifier: Apache-2.0 */
#include "bmi270.h"

static int16_t le16(const uint8_t *p) {
  return (int16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static int probe_id(bmi270_dev_t *dev) {
  uint8_t id = 0;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, BMI270_REG_CHIP_ID, &id, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (id != BMI270_CHIP_ID_VALUE) return RING_BUS_ERR_NO_DEV;
  return RING_BUS_OK;
}

int bmi270_soft_reset(bmi270_dev_t *dev) {
  uint8_t cmd = BMI270_CMD_SOFT_RESET;
  if (!dev || !dev->bus) return RING_BUS_ERR_INVAL;
  dev->ready = false;
  if (ring_i2c_reg_write(dev->bus, dev->addr7, BMI270_REG_CMD, &cmd, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  return RING_BUS_OK;
}

int bmi270_configure(bmi270_dev_t *dev, uint8_t acc_conf, uint8_t acc_range,
                     uint8_t gyr_conf, uint8_t gyr_range) {
  uint8_t pwr = 0x0E; /* acc+gyr on */
  if (!dev || !dev->bus) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_write(dev->bus, dev->addr7, BMI270_REG_ACC_CONF, &acc_conf, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (ring_i2c_reg_write(dev->bus, dev->addr7, BMI270_REG_ACC_RANGE, &acc_range, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (ring_i2c_reg_write(dev->bus, dev->addr7, BMI270_REG_GYR_CONF, &gyr_conf, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (ring_i2c_reg_write(dev->bus, dev->addr7, BMI270_REG_GYR_RANGE, &gyr_range, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (ring_i2c_reg_write(dev->bus, dev->addr7, BMI270_REG_PWR_CTRL, &pwr, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  dev->acc_conf = acc_conf;
  dev->acc_range = acc_range;
  dev->gyr_conf = gyr_conf;
  dev->gyr_range = gyr_range;
  return RING_BUS_OK;
}

int bmi270_init(bmi270_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7) {
  int rc;
  if (!dev || !bus) return RING_BUS_ERR_INVAL;
  dev->bus = bus;
  dev->addr7 = addr7 ? addr7 : BMI270_I2C_ADDR_DEFAULT;
  dev->ready = false;
  dev->sample_ok = 0;
  dev->sample_fail = 0;
  dev->recoveries = 0;
  dev->last_err = 0;
  rc = probe_id(dev);
  if (rc != RING_BUS_OK) return rc;
  rc = bmi270_configure(dev, BMI270_ACC_CONF_ODR100, BMI270_ACC_RANGE_8G,
                        BMI270_GYR_CONF_ODR100, BMI270_GYR_RANGE_2000);
  if (rc != RING_BUS_OK) return rc;
  dev->ready = true;
  return RING_BUS_OK;
}

int bmi270_recover(bmi270_dev_t *dev) {
  int rc;
  if (!dev) return RING_BUS_ERR_INVAL;
  (void)bmi270_soft_reset(dev);
  rc = bmi270_init(dev, dev->bus, dev->addr7);
  if (rc == RING_BUS_OK) dev->recoveries++;
  return rc;
}

int bmi270_sample(bmi270_dev_t *dev, bmi270_sample_t *out) {
  uint8_t raw[12];
  uint8_t err = 0;
  float acc_lsb, gyr_lsb;
  if (!dev || !out || !dev->ready) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, BMI270_REG_ERR_REG, &err, 1) != RING_BUS_OK) {
    dev->sample_fail++;
    return RING_BUS_ERR_IO;
  }
  dev->last_err = err;
  if (err != 0) {
    dev->sample_fail++;
    if (bmi270_recover(dev) != RING_BUS_OK) return RING_BUS_ERR_IO;
  }
  if (ring_i2c_reg_read(dev->bus, dev->addr7, BMI270_REG_ACC_X_LSB, raw, 6) != RING_BUS_OK) {
    dev->sample_fail++;
    return RING_BUS_ERR_IO;
  }
  if (ring_i2c_reg_read(dev->bus, dev->addr7, BMI270_REG_GYR_X_LSB, raw + 6, 6) != RING_BUS_OK) {
    dev->sample_fail++;
    return RING_BUS_ERR_IO;
  }
  /* ±8g → 4096 LSB/g; ±2000 dps → 16.4 LSB/dps (BMI270 defaults) */
  acc_lsb = 4096.0f;
  gyr_lsb = 16.4f;
  out->ax = (float)le16(raw + 0) / acc_lsb;
  out->ay = (float)le16(raw + 2) / acc_lsb;
  out->az = (float)le16(raw + 4) / acc_lsb;
  out->gx = (float)le16(raw + 6) / gyr_lsb;
  out->gy = (float)le16(raw + 8) / gyr_lsb;
  out->gz = (float)le16(raw + 10) / gyr_lsb;
  dev->sample_ok++;
  return RING_BUS_OK;
}

int bmi270_diagnostics(bmi270_dev_t *dev, bmi270_diag_t *out) {
  uint8_t id = 0, st = 0;
  if (!dev || !out) return RING_BUS_ERR_INVAL;
  out->ready = dev->ready;
  out->acc_conf = dev->acc_conf;
  out->gyr_conf = dev->gyr_conf;
  out->sample_ok = dev->sample_ok;
  out->sample_fail = dev->sample_fail;
  out->recoveries = dev->recoveries;
  out->err_reg = dev->last_err;
  out->chip_id = 0;
  out->status = 0;
  if (!dev->bus) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, BMI270_REG_CHIP_ID, &id, 1) == RING_BUS_OK)
    out->chip_id = id;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, BMI270_REG_STATUS, &st, 1) == RING_BUS_OK)
    out->status = st;
  return RING_BUS_OK;
}
