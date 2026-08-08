/* SPDX-License-Identifier: Apache-2.0 */
/*
 * Portable I2C/SPI bus abstraction for Edge I/O Ring digital firmware.
 * Host fake-bus, freestanding, and Zephyr backends implement this API.
 */
#ifndef RING_BUS_H
#define RING_BUS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
  RING_BUS_OK = 0,
  RING_BUS_ERR_IO = -1,
  RING_BUS_ERR_NACK = -2,
  RING_BUS_ERR_TIMEOUT = -3,
  RING_BUS_ERR_INVAL = -4,
  RING_BUS_ERR_NO_DEV = -5,
} ring_bus_status_t;

typedef struct ring_i2c_bus ring_i2c_bus_t;
typedef struct ring_spi_bus ring_spi_bus_t;

struct ring_i2c_bus {
  int (*write_read)(ring_i2c_bus_t *bus, uint8_t addr7,
                    const uint8_t *w, size_t wn,
                    uint8_t *r, size_t rn);
  int (*write)(ring_i2c_bus_t *bus, uint8_t addr7,
               const uint8_t *w, size_t wn);
  void *ctx;
};

struct ring_spi_bus {
  int (*xfer)(ring_spi_bus_t *bus, uint8_t cs_id,
              const uint8_t *tx, uint8_t *rx, size_t n);
  void *ctx;
};

static inline int ring_i2c_reg_read(ring_i2c_bus_t *bus, uint8_t addr7,
                                   uint8_t reg, uint8_t *out, size_t n) {
  if (!bus || !bus->write_read) return RING_BUS_ERR_INVAL;
  return bus->write_read(bus, addr7, &reg, 1, out, n);
}

static inline int ring_i2c_reg_write(ring_i2c_bus_t *bus, uint8_t addr7,
                                    uint8_t reg, const uint8_t *data, size_t n) {
  uint8_t buf[17];
  if (!bus || !bus->write || n > 16) return RING_BUS_ERR_INVAL;
  buf[0] = reg;
  for (size_t i = 0; i < n; i++) buf[1 + i] = data[i];
  return bus->write(bus, addr7, buf, n + 1);
}

#ifdef __cplusplus
}
#endif
#endif /* RING_BUS_H */
