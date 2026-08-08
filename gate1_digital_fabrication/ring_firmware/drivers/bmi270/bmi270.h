/* SPDX-License-Identifier: Apache-2.0 */
/* Register map aligned with Zephyr drivers/sensor/bosch/bmi270 (Apache-2.0). */
#ifndef RING_BMI270_H
#define RING_BMI270_H

#include "../bus/ring_bus.h"

#define BMI270_I2C_ADDR_DEFAULT 0x68
#define BMI270_REG_CHIP_ID      0x00
#define BMI270_REG_ACC_X_LSB    0x0C
#define BMI270_REG_GYR_X_LSB    0x12
#define BMI270_REG_PWR_CTRL     0x7D
#define BMI270_CHIP_ID_VALUE    0x24

typedef struct {
  float ax, ay, az;
  float gx, gy, gz;
} bmi270_sample_t;

typedef struct {
  ring_i2c_bus_t *bus;
  uint8_t addr7;
  bool ready;
} bmi270_dev_t;

int bmi270_init(bmi270_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7);
int bmi270_sample(bmi270_dev_t *dev, bmi270_sample_t *out);

#endif
