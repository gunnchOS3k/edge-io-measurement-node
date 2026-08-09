/* SPDX-License-Identifier: Apache-2.0 */
/*
 * Zephyr-native I2C/SPI bus backend for Edge I/O Ring.
 * Primary production path binds DEVICE_DT_GET / i2c_write_read / spi_transceive.
 * Compiled only under __ZEPHYR__; host CI proves structure via source gates.
 */
#ifndef RING_BUS_ZEPHYR_H
#define RING_BUS_ZEPHYR_H

#include "ring_bus.h"

#ifdef __cplusplus
extern "C" {
#endif

#if defined(__ZEPHYR__)
#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/drivers/spi.h>

typedef struct {
  ring_i2c_bus_t i2c;
  ring_spi_bus_t spi;
  const struct device *i2c_dev;
  const struct device *spi_dev;
  struct spi_config spi_cfg;
  struct spi_cs_control cs;
} ring_zephyr_bus_t;

int ring_zephyr_bus_bind(ring_zephyr_bus_t *zb,
                         const struct device *i2c_dev,
                         const struct device *spi_dev);
#else
/* Host/structural stub: symbols exist for freestanding linkage proofs. */
typedef struct {
  ring_i2c_bus_t i2c;
  ring_spi_bus_t spi;
  void *i2c_dev;
  void *spi_dev;
} ring_zephyr_bus_t;

int ring_zephyr_bus_bind(ring_zephyr_bus_t *zb, void *i2c_dev, void *spi_dev);
#endif

#ifdef __cplusplus
}
#endif
#endif /* RING_BUS_ZEPHYR_H */
