/* SPDX-License-Identifier: Apache-2.0 */
#ifndef RING_BUS_FAKE_H
#define RING_BUS_FAKE_H
#include "ring_bus.h"

typedef enum {
  RING_FAKE_MODE_HEALTHY = 0,
  RING_FAKE_MODE_INIT_FAIL_IMU,
  RING_FAKE_MODE_INVALID_SENSOR,
  RING_FAKE_MODE_LOW_BATTERY,
  RING_FAKE_MODE_PACKET_LOSS,
  RING_FAKE_MODE_REPLAY,
} ring_fake_mode_t;

typedef struct {
  ring_i2c_bus_t i2c;
  ring_spi_bus_t spi;
  ring_fake_mode_t mode;
  uint32_t sample_count;
  uint32_t drop_every_n; /* packet loss */
  uint32_t last_seq_seen; /* replay detection helper */
  uint32_t write_count;
  uint8_t last_write_addr;
  uint8_t last_write_reg;
  uint8_t se_challenge[16];
} ring_fake_bus_t;

void ring_fake_bus_init(ring_fake_bus_t *fb, ring_fake_mode_t mode);
#endif
