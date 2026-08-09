/* SPDX-License-Identifier: Apache-2.0 */
/* Register map aligned with Zephyr drivers/sensor/bosch/bmi270 (Apache-2.0). */
#ifndef RING_BMI270_H
#define RING_BMI270_H

#include "../bus/ring_bus.h"

#define BMI270_I2C_ADDR_DEFAULT 0x68
#define BMI270_REG_CHIP_ID      0x00
#define BMI270_REG_ERR_REG      0x02
#define BMI270_REG_STATUS       0x03
#define BMI270_REG_ACC_X_LSB    0x0C
#define BMI270_REG_GYR_X_LSB    0x12
#define BMI270_REG_ACC_CONF     0x40
#define BMI270_REG_ACC_RANGE    0x41
#define BMI270_REG_GYR_CONF     0x42
#define BMI270_REG_GYR_RANGE    0x43
#define BMI270_REG_CMD          0x7E
#define BMI270_REG_PWR_CTRL     0x7D
#define BMI270_CHIP_ID_VALUE    0x24
#define BMI270_CMD_SOFT_RESET   0xB6
#define BMI270_ACC_CONF_ODR100  0xA8 /* filter + ODR 100 Hz stand-in */
#define BMI270_ACC_RANGE_8G     0x02
#define BMI270_GYR_CONF_ODR100  0xA9
#define BMI270_GYR_RANGE_2000   0x00

typedef struct {
  float ax, ay, az;
  float gx, gy, gz;
} bmi270_sample_t;

typedef struct {
  uint8_t chip_id;
  uint8_t err_reg;
  uint8_t status;
  uint8_t acc_conf;
  uint8_t gyr_conf;
  uint32_t sample_ok;
  uint32_t sample_fail;
  uint32_t recoveries;
  bool ready;
} bmi270_diag_t;

typedef struct {
  ring_i2c_bus_t *bus;
  uint8_t addr7;
  bool ready;
  uint8_t acc_conf;
  uint8_t gyr_conf;
  uint8_t acc_range;
  uint8_t gyr_range;
  uint32_t sample_ok;
  uint32_t sample_fail;
  uint32_t recoveries;
  uint8_t last_err;
} bmi270_dev_t;

int bmi270_init(bmi270_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7);
int bmi270_configure(bmi270_dev_t *dev, uint8_t acc_conf, uint8_t acc_range,
                     uint8_t gyr_conf, uint8_t gyr_range);
int bmi270_soft_reset(bmi270_dev_t *dev);
int bmi270_recover(bmi270_dev_t *dev);
int bmi270_sample(bmi270_dev_t *dev, bmi270_sample_t *out);
int bmi270_diagnostics(bmi270_dev_t *dev, bmi270_diag_t *out);

#endif
