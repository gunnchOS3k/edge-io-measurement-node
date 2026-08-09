/* SPDX-License-Identifier: Apache-2.0 */
/*
 * NXP SE050C1 identity/auth digital path.
 * Full Plug&Trust MW is large/vendor-licensed; this driver implements an
 * I2C ATR/identity probe + bus-backed challenge/response for digital bring-up.
 * NOT production SE050 crypto.
 */
#ifndef RING_SE050_H
#define RING_SE050_H

#include "../bus/ring_bus.h"

#define SE050_I2C_ADDR_DEFAULT 0x48
#define SE050_REG_ATR          0xA5
#define SE050_REG_CHALLENGE    0xB0
#define SE050_REG_RESPONSE     0xB1
#define SE050_REG_CTRL         0xC0
#define SE050_ATR_MARK         0x5E
#define SE050_CTRL_RESET       0x01

typedef struct {
  uint8_t atr[8];
  uint8_t device_uid[16];
  bool authenticated;
} se050_identity_t;

typedef struct {
  uint8_t atr0;
  uint8_t uid0;
  uint32_t auth_ok;
  uint32_t auth_fail;
  uint32_t recoveries;
  bool ready;
} se050_diag_t;

typedef struct {
  ring_i2c_bus_t *bus;
  uint8_t addr7;
  bool ready;
  uint8_t session_key[16];
  uint32_t auth_ok;
  uint32_t auth_fail;
  uint32_t recoveries;
} se050_dev_t;

int se050_init(se050_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7);
int se050_soft_reset(se050_dev_t *dev);
int se050_recover(se050_dev_t *dev);
int se050_read_identity(se050_dev_t *dev, se050_identity_t *out);
int se050_auth_challenge(se050_dev_t *dev, const uint8_t challenge[16],
                         uint8_t response[16]);
int se050_diagnostics(se050_dev_t *dev, se050_diag_t *out);

#endif
