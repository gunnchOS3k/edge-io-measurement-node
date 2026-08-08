/* SPDX-License-Identifier: Apache-2.0 */
#include "ring_bus_fake.h"
#include <string.h>

static ring_fake_bus_t *as_fb(ring_i2c_bus_t *bus) {
  return (ring_fake_bus_t *)bus->ctx;
}

static int fake_i2c_write_read(ring_i2c_bus_t *bus, uint8_t addr7,
                               const uint8_t *w, size_t wn,
                               uint8_t *r, size_t rn) {
  ring_fake_bus_t *fb = as_fb(bus);
  uint8_t reg;
  if (!fb || !w || wn < 1) return RING_BUS_ERR_INVAL;
  reg = w[0];
  memset(r, 0, rn);

  if (fb->mode == RING_FAKE_MODE_INIT_FAIL_IMU && addr7 == 0x68)
    return RING_BUS_ERR_NACK;

  if (addr7 == 0x68) { /* BMI270 */
    if (fb->mode == RING_FAKE_MODE_INVALID_SENSOR && reg == 0x00) {
      if (rn) r[0] = 0xFF;
      return RING_BUS_OK;
    }
    if (reg == 0x00 && rn) { r[0] = 0x24; return RING_BUS_OK; }
    if (reg == 0x0C && rn >= 6) {
      /* az ~ 1g */
      r[4] = 0x00; r[5] = 0x10;
      return RING_BUS_OK;
    }
    if (reg == 0x12 && rn >= 6) return RING_BUS_OK;
    return RING_BUS_OK;
  }
  if (addr7 == 0x44) { /* IQS7222A */
    if (reg == 0x00 && rn) { r[0] = 0x42; return RING_BUS_OK; }
    if (reg == 0x10 && rn) { r[0] = 0x01; return RING_BUS_OK; }
    if (reg == 0x11 && rn) { r[0] = 0x03; return RING_BUS_OK; }
    return RING_BUS_OK;
  }
  if (addr7 == 0x48) { /* SE050 */
    if (reg == 0xA5) {
      if (rn >= 1) r[0] = 0x5E;
      for (size_t i = 1; i < rn && i < 8; i++) r[i] = (uint8_t)(0x10 + i);
      for (size_t i = 8; i < rn && i < 24; i++) r[i] = (uint8_t)(0xE0 + (i - 8));
      return RING_BUS_OK;
    }
    return RING_BUS_OK;
  }
  if (addr7 == 0x6B) { /* npm1300 */
    if (reg == 0x7F && rn) { r[0] = 0x13; return RING_BUS_OK; }
    if (reg == 0x10 && rn) {
      uint16_t mv = (fb->mode == RING_FAKE_MODE_LOW_BATTERY) ? 3350 : 3900;
      r[0] = (uint8_t)(mv >> 8);
      return RING_BUS_OK;
    }
    if (reg == 0x11 && rn) {
      uint16_t mv = (fb->mode == RING_FAKE_MODE_LOW_BATTERY) ? 3350 : 3900;
      r[0] = (uint8_t)(mv & 0xFF);
      return RING_BUS_OK;
    }
    if (reg == 0x02 && rn) { r[0] = 0x01; return RING_BUS_OK; }
    return RING_BUS_OK;
  }
  if (addr7 == 0x14) { /* BMM350 */
    if (reg == 0x00 && rn) { r[0] = 0x33; return RING_BUS_OK; }
    return RING_BUS_OK;
  }
  return RING_BUS_ERR_NACK;
}

static int fake_i2c_write(ring_i2c_bus_t *bus, uint8_t addr7,
                          const uint8_t *w, size_t wn) {
  (void)bus; (void)addr7; (void)w; (void)wn;
  return RING_BUS_OK;
}

static int fake_spi_xfer(ring_spi_bus_t *bus, uint8_t cs_id,
                         const uint8_t *tx, uint8_t *rx, size_t n) {
  ring_fake_bus_t *fb = (ring_fake_bus_t *)bus->ctx;
  (void)cs_id;
  if (!fb || !tx || !rx || n < 2) return RING_BUS_ERR_INVAL;
  memset(rx, 0, n);
  if (tx[0] == 0x00) { rx[1] = 0xDE; return RING_BUS_OK; }
  if (tx[0] == 0x01 && n >= 5) {
    rx[1] = 0xE8; rx[2] = 0x03; /* 1000 mm */
    return RING_BUS_OK;
  }
  return RING_BUS_OK;
}

void ring_fake_bus_init(ring_fake_bus_t *fb, ring_fake_mode_t mode) {
  memset(fb, 0, sizeof(*fb));
  fb->mode = mode;
  fb->drop_every_n = (mode == RING_FAKE_MODE_PACKET_LOSS) ? 3 : 0;
  fb->i2c.write_read = fake_i2c_write_read;
  fb->i2c.write = fake_i2c_write;
  fb->i2c.ctx = fb;
  fb->spi.xfer = fake_spi_xfer;
  fb->spi.ctx = fb;
}
