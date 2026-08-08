/* SPDX-License-Identifier: Apache-2.0 */
#ifndef RING_BMM350_H
#define RING_BMM350_H
#include "../bus/ring_bus.h"
#define BMM350_I2C_ADDR_DEFAULT 0x14
#define BMM350_REG_CHIP_ID 0x00
#define BMM350_CHIP_ID_VALUE 0x33
typedef struct { float mx, my, mz; } bmm350_sample_t;
typedef struct { ring_i2c_bus_t *bus; uint8_t addr7; bool ready; bool enabled; } bmm350_dev_t;
int bmm350_init(bmm350_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7, bool enabled);
int bmm350_sample(bmm350_dev_t *dev, bmm350_sample_t *out);
#endif
