/* SPDX-License-Identifier: Apache-2.0 */
/*
 * Nordic nPM1300 PMIC — portable digital driver.
 * Register conventions aligned with Zephyr mfd/npm1300 + charger (Apache-2.0).
 */
#ifndef RING_NPM1300_H
#define RING_NPM1300_H

#include "../bus/ring_bus.h"

#define NPM1300_I2C_ADDR_DEFAULT 0x6B
#define NPM1300_REG_MAIN_EVENTS  0x00
#define NPM1300_REG_VBUSIN_STATUS 0x02
#define NPM1300_REG_ADC_VBAT_MSB 0x10
#define NPM1300_REG_ADC_VBAT_LSB 0x11
#define NPM1300_REG_SHIP_STATUS  0x20
#define NPM1300_REG_ADC_CONFIG   0x30
#define NPM1300_REG_BCHG_ERR     0x40
#define NPM1300_REG_RESET        0x50
#define NPM1300_MARK_REG         0x7F
#define NPM1300_MARK_VALUE       0x13
#define NPM1300_ADC_CFG_ENABLE   0x01
#define NPM1300_RESET_SOFT       0x01

typedef struct {
  uint16_t vbat_mv;
  uint8_t soc_pct;
  bool vbus_present;
  bool charging;
  uint8_t charger_err;
} npm1300_status_t;

typedef struct {
  uint8_t mark;
  uint8_t adc_config;
  uint32_t read_ok;
  uint32_t read_fail;
  uint32_t recoveries;
  bool ready;
} npm1300_diag_t;

typedef struct {
  ring_i2c_bus_t *bus;
  uint8_t addr7;
  bool ready;
  uint8_t adc_config;
  uint32_t read_ok;
  uint32_t read_fail;
  uint32_t recoveries;
} npm1300_dev_t;

int npm1300_init(npm1300_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7);
int npm1300_configure(npm1300_dev_t *dev, uint8_t adc_config);
int npm1300_soft_reset(npm1300_dev_t *dev);
int npm1300_recover(npm1300_dev_t *dev);
int npm1300_read_status(npm1300_dev_t *dev, npm1300_status_t *out);
int npm1300_diagnostics(npm1300_dev_t *dev, npm1300_diag_t *out);

#endif
