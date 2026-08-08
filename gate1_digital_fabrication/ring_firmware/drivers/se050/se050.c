/* SPDX-License-Identifier: Apache-2.0 */
#include "se050.h"

int se050_init(se050_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7) {
  uint8_t atr = 0;
  if (!dev || !bus) return RING_BUS_ERR_INVAL;
  dev->bus = bus;
  dev->addr7 = addr7 ? addr7 : SE050_I2C_ADDR_DEFAULT;
  dev->ready = false;
  for (int i = 0; i < 16; i++) dev->session_key[i] = (uint8_t)(0xC0 + i);
  if (ring_i2c_reg_read(bus, dev->addr7, SE050_REG_ATR, &atr, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (atr != SE050_ATR_MARK) return RING_BUS_ERR_NO_DEV;
  dev->ready = true;
  return RING_BUS_OK;
}

int se050_read_identity(se050_dev_t *dev, se050_identity_t *out) {
  uint8_t buf[24];
  if (!dev || !out || !dev->ready) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, SE050_REG_ATR, buf, 24) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  for (int i = 0; i < 8; i++) out->atr[i] = buf[i];
  for (int i = 0; i < 16; i++) out->device_uid[i] = buf[8 + i];
  out->authenticated = false;
  return RING_BUS_OK;
}

int se050_auth_challenge(se050_dev_t *dev, const uint8_t challenge[16],
                         uint8_t response[16]) {
  if (!dev || !challenge || !response || !dev->ready) return RING_BUS_ERR_INVAL;
  /* Development keyed response — NOT production SE050 crypto. */
  for (int i = 0; i < 16; i++)
    response[i] = (uint8_t)(challenge[i] ^ dev->session_key[i] ^ 0x5A);
  return RING_BUS_OK;
}
