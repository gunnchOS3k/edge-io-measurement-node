/* SPDX-License-Identifier: Apache-2.0 */
#include "bmi270.h"

static int16_t le16(const uint8_t *p) {
  return (int16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

int bmi270_init(bmi270_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7) {
  uint8_t id = 0;
  uint8_t pwr = 0x0E; /* acc+gyr on */
  if (!dev || !bus) return RING_BUS_ERR_INVAL;
  dev->bus = bus;
  dev->addr7 = addr7 ? addr7 : BMI270_I2C_ADDR_DEFAULT;
  dev->ready = false;
  if (ring_i2c_reg_read(bus, dev->addr7, BMI270_REG_CHIP_ID, &id, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (id != BMI270_CHIP_ID_VALUE) return RING_BUS_ERR_NO_DEV;
  if (ring_i2c_reg_write(bus, dev->addr7, BMI270_REG_PWR_CTRL, &pwr, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  dev->ready = true;
  return RING_BUS_OK;
}

int bmi270_sample(bmi270_dev_t *dev, bmi270_sample_t *out) {
  uint8_t raw[12];
  if (!dev || !out || !dev->ready) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, BMI270_REG_ACC_X_LSB, raw, 6) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, BMI270_REG_GYR_X_LSB, raw + 6, 6) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  /* ±8g / ±2000 dps scale stand-in matching typical BMI270 defaults */
  out->ax = (float)le16(raw + 0) / 4096.0f;
  out->ay = (float)le16(raw + 2) / 4096.0f;
  out->az = (float)le16(raw + 4) / 4096.0f;
  out->gx = (float)le16(raw + 6) / 16.4f;
  out->gy = (float)le16(raw + 8) / 16.4f;
  out->gz = (float)le16(raw + 10) / 16.4f;
  return RING_BUS_OK;
}
