/* SPDX-License-Identifier: Apache-2.0 */
/*
 * Azoteq IQS7222A capacitive controller — portable digital driver.
 * No upstream Zephyr driver; register map from public datasheet defaults.
 */
#ifndef RING_IQS7222A_H
#define RING_IQS7222A_H

#include "../bus/ring_bus.h"

#define IQS7222A_I2C_ADDR_DEFAULT 0x44
#define IQS7222A_REG_PROD_NUM     0x00
#define IQS7222A_REG_VERSION      0x01
#define IQS7222A_REG_SYS_STATUS   0x10
#define IQS7222A_REG_TOUCH_FLAGS  0x11
#define IQS7222A_REG_CH_COUNT_LSB 0x12
#define IQS7222A_REG_CH_COUNT_MSB 0x13
#define IQS7222A_REG_SYS_CONTROL  0x20
#define IQS7222A_PROD_NUM_EXPECT  0x42
#define IQS7222A_SYS_CTRL_ATI     0x01
#define IQS7222A_SYS_CTRL_RESET   0x80

typedef struct {
  uint8_t touch_flags;
  uint8_t sys_status;
  bool proximity;
  bool touch;
  uint16_t channel_count;
  float strength; /* 0..1 normalized from channel counts */
} iqs7222a_state_t;

typedef struct {
  uint8_t prod;
  uint8_t version;
  uint8_t sys_control;
  uint32_t read_ok;
  uint32_t read_fail;
  uint32_t recoveries;
  bool ready;
} iqs7222a_diag_t;

typedef struct {
  ring_i2c_bus_t *bus;
  uint8_t addr7;
  bool ready;
  uint8_t sys_control;
  uint32_t read_ok;
  uint32_t read_fail;
  uint32_t recoveries;
} iqs7222a_dev_t;

int iqs7222a_init(iqs7222a_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7);
int iqs7222a_configure(iqs7222a_dev_t *dev, uint8_t sys_control);
int iqs7222a_soft_reset(iqs7222a_dev_t *dev);
int iqs7222a_recover(iqs7222a_dev_t *dev);
int iqs7222a_read_state(iqs7222a_dev_t *dev, iqs7222a_state_t *out);
int iqs7222a_diagnostics(iqs7222a_dev_t *dev, iqs7222a_diag_t *out);

#endif
