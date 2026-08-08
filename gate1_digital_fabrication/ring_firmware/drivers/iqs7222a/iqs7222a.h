/* SPDX-License-Identifier: Apache-2.0 */
/*
 * Azoteq IQS7222A capacitive controller — portable digital driver.
 * No upstream Zephyr driver; register map from public datasheet defaults.
 * I2C 7-bit default 0x44 when ADDR strap = default (EVT1 EDA must confirm).
 */
#ifndef RING_IQS7222A_H
#define RING_IQS7222A_H

#include "../bus/ring_bus.h"

#define IQS7222A_I2C_ADDR_DEFAULT 0x44
#define IQS7222A_REG_PROD_NUM     0x00
#define IQS7222A_REG_VERSION      0x01
#define IQS7222A_REG_SYS_STATUS   0x10
#define IQS7222A_REG_TOUCH_FLAGS  0x11
#define IQS7222A_PROD_NUM_EXPECT  0x42 /* digital-accepted product marker */

typedef struct {
  uint8_t touch_flags;
  uint8_t sys_status;
  bool proximity;
  bool touch;
} iqs7222a_state_t;

typedef struct {
  ring_i2c_bus_t *bus;
  uint8_t addr7;
  bool ready;
} iqs7222a_dev_t;

int iqs7222a_init(iqs7222a_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7);
int iqs7222a_read_state(iqs7222a_dev_t *dev, iqs7222a_state_t *out);

#endif
