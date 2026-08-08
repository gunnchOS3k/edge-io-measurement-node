/* SPDX-License-Identifier: Apache-2.0 */
/*
 * NXP SE050C1 identity/auth digital path.
 * Full Plug&Trust MW is large/vendor-licensed; this driver implements a
 * documented I2C T=1-style ATR/identity probe + challenge-response mint
 * suitable for digital bring-up. Default 7-bit addr 0x48 (NXP default).
 */
#ifndef RING_SE050_H
#define RING_SE050_H

#include "../bus/ring_bus.h"

#define SE050_I2C_ADDR_DEFAULT 0x48
#define SE050_REG_ATR          0xA5
#define SE050_ATR_MARK         0x5E /* digital ATR marker */

typedef struct {
  uint8_t atr[8];
  uint8_t device_uid[16];
  bool authenticated;
} se050_identity_t;

typedef struct {
  ring_i2c_bus_t *bus;
  uint8_t addr7;
  bool ready;
  uint8_t session_key[16];
} se050_dev_t;

int se050_init(se050_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7);
int se050_read_identity(se050_dev_t *dev, se050_identity_t *out);
int se050_auth_challenge(se050_dev_t *dev, const uint8_t challenge[16],
                         uint8_t response[16]);

#endif
