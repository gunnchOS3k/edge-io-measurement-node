/* SPDX-License-Identifier: Apache-2.0 */
#ifndef RING_APP_H
#define RING_APP_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "../drivers/bus/ring_bus.h"

#ifndef RING_FEATURE_UWB
#define RING_FEATURE_UWB 0
#endif
#ifndef RING_FEATURE_MAG
#define RING_FEATURE_MAG 0
#endif

typedef struct {
  uint64_t ts_ms;
  float ax, ay, az, gx, gy, gz;
  float confidence;
  uint8_t cap_flags;
  bool cap_touch;
  bool cap_prox;
  uint8_t batt_pct;
  uint16_t vbat_mv;
  uint8_t se_uid[16];
  bool se_auth_ok;
  uint32_t seq;
  uint8_t mac[16];
  uint32_t uwb_range_mm;
  bool uwb_ok;
  float mx, my, mz;
  uint8_t dfu_state; /* 0 idle 1 pending 2 validating */
  uint8_t health;    /* bitflags */
  float cal_conf;
  bool ble_paired;
  bool low_battery;
} ring_fusion_frame_t;

typedef struct {
  ring_i2c_bus_t *i2c;
  ring_spi_bus_t *spi;
  bool uwb_populated;
  bool mag_enabled;
  const uint8_t *session_key; /* 16 bytes */
} ring_app_cfg_t;

typedef struct ring_app ring_app_t;

int ring_app_init(ring_app_t *app, const ring_app_cfg_t *cfg);
int ring_app_boot_diagnostics(ring_app_t *app, char *buf, size_t n);
int ring_app_tick(ring_app_t *app, uint64_t ts_ms, ring_fusion_frame_t *frame);
int ring_app_calibrate_step(ring_app_t *app);
int ring_app_set_dfu_state(ring_app_t *app, uint8_t state);
int ring_app_ble_pair(ring_app_t *app);
int ring_app_health_telemetry(ring_app_t *app, char *buf, size_t n);
bool ring_app_ready(const ring_app_t *app);
const char *ring_app_last_error(const ring_app_t *app);

/* Opaque size for stack alloc */
struct ring_app {
  ring_app_cfg_t cfg;
  int imu_ok, cap_ok, se_ok, pmic_ok, uwb_ok, mag_ok;
  uint32_t seq;
  float cal_conf;
  uint8_t dfu_state;
  int ble_paired;
  uint8_t batt_pct;
  char last_error[64];
  uint8_t key[16];
  /* driver storage */
  uint8_t drv_storage[512];
};

#endif
