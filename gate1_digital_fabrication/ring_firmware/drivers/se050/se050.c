/* SPDX-License-Identifier: Apache-2.0 */
#include "se050.h"

int se050_soft_reset(se050_dev_t *dev) {
  uint8_t ctrl = SE050_CTRL_RESET;
  if (!dev || !dev->bus) return RING_BUS_ERR_INVAL;
  dev->ready = false;
  return ring_i2c_reg_write(dev->bus, dev->addr7, SE050_REG_CTRL, &ctrl, 1);
}

int se050_init(se050_dev_t *dev, ring_i2c_bus_t *bus, uint8_t addr7) {
  uint8_t atr = 0;
  if (!dev || !bus) return RING_BUS_ERR_INVAL;
  dev->bus = bus;
  dev->addr7 = addr7 ? addr7 : SE050_I2C_ADDR_DEFAULT;
  dev->ready = false;
  dev->auth_ok = 0;
  dev->auth_fail = 0;
  dev->recoveries = 0;
  for (int i = 0; i < 16; i++) dev->session_key[i] = (uint8_t)(0xC0 + i);
  if (ring_i2c_reg_read(bus, dev->addr7, SE050_REG_ATR, &atr, 1) != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  if (atr != SE050_ATR_MARK) return RING_BUS_ERR_NO_DEV;
  /* Seed session material into secure-element register window (DEV only). */
  if (ring_i2c_reg_write(bus, dev->addr7, SE050_REG_CHALLENGE, dev->session_key, 16)
      != RING_BUS_OK)
    return RING_BUS_ERR_IO;
  dev->ready = true;
  return RING_BUS_OK;
}

int se050_recover(se050_dev_t *dev) {
  int rc;
  if (!dev) return RING_BUS_ERR_INVAL;
  (void)se050_soft_reset(dev);
  rc = se050_init(dev, dev->bus, dev->addr7);
  if (rc == RING_BUS_OK) dev->recoveries++;
  return rc;
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
  uint8_t rx[16];
  if (!dev || !challenge || !response || !dev->ready) return RING_BUS_ERR_INVAL;
  /* Bus transaction path: write challenge, read SE response register. */
  if (ring_i2c_reg_write(dev->bus, dev->addr7, SE050_REG_CHALLENGE, challenge, 16)
      != RING_BUS_OK) {
    dev->auth_fail++;
    return RING_BUS_ERR_IO;
  }
  if (ring_i2c_reg_read(dev->bus, dev->addr7, SE050_REG_RESPONSE, rx, 16) != RING_BUS_OK) {
    dev->auth_fail++;
    (void)se050_recover(dev);
    return RING_BUS_ERR_IO;
  }
  /* Development keyed mint over bus response — NOT production SE050 crypto. */
  for (int i = 0; i < 16; i++)
    response[i] = (uint8_t)(rx[i] ^ challenge[i] ^ dev->session_key[i] ^ 0x5A);
  dev->auth_ok++;
  return RING_BUS_OK;
}

int se050_diagnostics(se050_dev_t *dev, se050_diag_t *out) {
  uint8_t atr[9];
  if (!dev || !out) return RING_BUS_ERR_INVAL;
  out->ready = dev->ready;
  out->auth_ok = dev->auth_ok;
  out->auth_fail = dev->auth_fail;
  out->recoveries = dev->recoveries;
  out->atr0 = 0;
  out->uid0 = 0;
  if (!dev->bus) return RING_BUS_ERR_INVAL;
  if (ring_i2c_reg_read(dev->bus, dev->addr7, SE050_REG_ATR, atr, 9) == RING_BUS_OK) {
    out->atr0 = atr[0];
    out->uid0 = atr[8];
  }
  return RING_BUS_OK;
}
