/* SPDX-License-Identifier: Apache-2.0 */
#include "ring_bus_zephyr.h"
#include <string.h>

#if defined(__ZEPHYR__)

static int z_i2c_write_read(ring_i2c_bus_t *bus, uint8_t addr7,
                            const uint8_t *w, size_t wn,
                            uint8_t *r, size_t rn) {
  ring_zephyr_bus_t *zb = (ring_zephyr_bus_t *)bus->ctx;
  if (!zb || !zb->i2c_dev || !device_is_ready(zb->i2c_dev))
    return RING_BUS_ERR_NO_DEV;
  if (i2c_write_read(zb->i2c_dev, addr7, w, wn, r, rn) != 0)
    return RING_BUS_ERR_IO;
  return RING_BUS_OK;
}

static int z_i2c_write(ring_i2c_bus_t *bus, uint8_t addr7,
                       const uint8_t *w, size_t wn) {
  ring_zephyr_bus_t *zb = (ring_zephyr_bus_t *)bus->ctx;
  if (!zb || !zb->i2c_dev || !device_is_ready(zb->i2c_dev))
    return RING_BUS_ERR_NO_DEV;
  if (i2c_write(zb->i2c_dev, w, wn, addr7) != 0)
    return RING_BUS_ERR_IO;
  return RING_BUS_OK;
}

static int z_spi_xfer(ring_spi_bus_t *bus, uint8_t cs_id,
                      const uint8_t *tx, uint8_t *rx, size_t n) {
  ring_zephyr_bus_t *zb = (ring_zephyr_bus_t *)bus->ctx;
  struct spi_buf txb = {.buf = (void *)tx, .len = n};
  struct spi_buf rxb = {.buf = rx, .len = n};
  struct spi_buf_set txs = {.buffers = &txb, .count = 1};
  struct spi_buf_set rxs = {.buffers = &rxb, .count = 1};
  (void)cs_id;
  if (!zb || !zb->spi_dev || !device_is_ready(zb->spi_dev))
    return RING_BUS_ERR_NO_DEV;
  if (spi_transceive(zb->spi_dev, &zb->spi_cfg, &txs, &rxs) != 0)
    return RING_BUS_ERR_IO;
  return RING_BUS_OK;
}

int ring_zephyr_bus_bind(ring_zephyr_bus_t *zb,
                         const struct device *i2c_dev,
                         const struct device *spi_dev) {
  if (!zb) return RING_BUS_ERR_INVAL;
  memset(zb, 0, sizeof(*zb));
  zb->i2c_dev = i2c_dev;
  zb->spi_dev = spi_dev;
  zb->i2c.write_read = z_i2c_write_read;
  zb->i2c.write = z_i2c_write;
  zb->i2c.ctx = zb;
  zb->spi.xfer = z_spi_xfer;
  zb->spi.ctx = zb;
  zb->spi_cfg.frequency = 8000000;
  zb->spi_cfg.operation = SPI_OP_MODE_MASTER | SPI_WORD_SET(8);
  return RING_BUS_OK;
}

#else /* host / structural */

int ring_zephyr_bus_bind(ring_zephyr_bus_t *zb, void *i2c_dev, void *spi_dev) {
  if (!zb) return RING_BUS_ERR_INVAL;
  memset(zb, 0, sizeof(*zb));
  zb->i2c_dev = i2c_dev;
  zb->spi_dev = spi_dev;
  /* Without Zephyr devices, leave ops NULL — native path must not run on host. */
  return RING_BUS_OK;
}

#endif
