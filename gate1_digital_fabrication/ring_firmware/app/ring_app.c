/* SPDX-License-Identifier: Apache-2.0 */
#include "ring_app.h"
#include "../drivers/bmi270/bmi270.h"
#include "../drivers/iqs7222a/iqs7222a.h"
#include "../drivers/se050/se050.h"
#include "../drivers/npm1300/npm1300.h"
#include "../drivers/dw3000/dw3000.h"
#include "../drivers/bmm350/bmm350.h"
#include <stdio.h>
#include <string.h>

typedef struct {
  bmi270_dev_t imu;
  iqs7222a_dev_t cap;
  se050_dev_t se;
  npm1300_dev_t pmic;
  dw3000_dev_t uwb;
  bmm350_dev_t mag;
} ring_drivers_t;

static ring_drivers_t *drv(ring_app_t *app) {
  return (ring_drivers_t *)app->drv_storage;
}

static void set_err(ring_app_t *app, const char *msg) {
  size_t i = 0;
  if (!app) return;
  for (; msg[i] && i + 1 < sizeof(app->last_error); i++)
    app->last_error[i] = msg[i];
  app->last_error[i] = 0;
}

static void mint_mac(const uint8_t key[16], uint32_t seq, uint64_t ts, uint8_t out[16]) {
  for (int i = 0; i < 16; i++)
    out[i] = (uint8_t)(key[i] ^ (seq + i * 13) ^ (uint8_t)(ts >> (i % 8)) ^ 0xA5);
}

int ring_app_init(ring_app_t *app, const ring_app_cfg_t *cfg) {
  ring_drivers_t *d;
  if (!app || !cfg || !cfg->i2c) return -1;
  memset(app, 0, sizeof(*app));
  app->cfg = *cfg;
  if (cfg->session_key) memcpy(app->key, cfg->session_key, 16);
  else for (int i = 0; i < 16; i++) app->key[i] = (uint8_t)i;
  d = drv(app);
  memset(d, 0, sizeof(*d));

  app->imu_ok = bmi270_init(&d->imu, cfg->i2c, BMI270_I2C_ADDR_DEFAULT);
  if (app->imu_ok != RING_BUS_OK) set_err(app, "bmi270_init_fail");

  app->cap_ok = iqs7222a_init(&d->cap, cfg->i2c, IQS7222A_I2C_ADDR_DEFAULT);
  if (app->cap_ok != RING_BUS_OK) set_err(app, "iqs7222a_init_fail");

  app->se_ok = se050_init(&d->se, cfg->i2c, SE050_I2C_ADDR_DEFAULT);
  if (app->se_ok != RING_BUS_OK) set_err(app, "se050_init_fail");

  app->pmic_ok = npm1300_init(&d->pmic, cfg->i2c, NPM1300_I2C_ADDR_DEFAULT);
  if (app->pmic_ok != RING_BUS_OK) set_err(app, "npm1300_init_fail");

  app->uwb_ok = dw3000_init(&d->uwb, cfg->spi, DW3000_CS_ID_DEFAULT,
                            cfg->uwb_populated || RING_FEATURE_UWB);
  if (cfg->uwb_populated && app->uwb_ok != RING_BUS_OK) set_err(app, "dw3000_init_fail");

  app->mag_ok = bmm350_init(&d->mag, cfg->i2c, BMM350_I2C_ADDR_DEFAULT,
                            cfg->mag_enabled || RING_FEATURE_MAG);
  if ((cfg->mag_enabled || RING_FEATURE_MAG) && app->mag_ok != RING_BUS_OK)
    set_err(app, "bmm350_init_fail");

  app->seq = 1;
  return (app->imu_ok == RING_BUS_OK && app->cap_ok == RING_BUS_OK &&
          app->se_ok == RING_BUS_OK && app->pmic_ok == RING_BUS_OK)
             ? 0
             : -2;
}

bool ring_app_ready(const ring_app_t *app) {
  return app && app->imu_ok == 0 && app->cap_ok == 0 && app->se_ok == 0 && app->pmic_ok == 0;
}

const char *ring_app_last_error(const ring_app_t *app) {
  return app ? app->last_error : "null";
}

int ring_app_boot_diagnostics(ring_app_t *app, char *buf, size_t n) {
  if (!app || !buf || !n) return -1;
  snprintf(buf, n,
           "boot diag imu=%d cap=%d se=%d pmic=%d uwb=%d mag=%d err=%s",
           app->imu_ok, app->cap_ok, app->se_ok, app->pmic_ok, app->uwb_ok,
           app->mag_ok, app->last_error[0] ? app->last_error : "none");
  return 0;
}

int ring_app_calibrate_step(ring_app_t *app) {
  if (!app) return -1;
  if (app->cal_conf < 1.0f) app->cal_conf += 0.25f;
  if (app->cal_conf > 1.0f) app->cal_conf = 1.0f;
  return 0;
}

int ring_app_set_dfu_state(ring_app_t *app, uint8_t state) {
  if (!app || state > 2) return -1;
  app->dfu_state = state;
  return 0;
}

int ring_app_ble_pair(ring_app_t *app) {
  if (!app) return -1;
  app->ble_paired = 1;
  return 0;
}

int ring_app_tick(ring_app_t *app, uint64_t ts_ms, ring_fusion_frame_t *frame) {
  ring_drivers_t *d;
  bmi270_sample_t imu;
  iqs7222a_state_t cap;
  npm1300_status_t batt;
  se050_identity_t ident;
  uint8_t challenge[16], response[16];
  dw3000_range_t rng;
  bmm350_sample_t mag;
  if (!app || !frame) return -1;
  if (!ring_app_ready(app)) return -2;
  d = drv(app);
  memset(frame, 0, sizeof(*frame));
  frame->ts_ms = ts_ms;
  frame->seq = app->seq++;
  frame->cal_conf = app->cal_conf;
  frame->dfu_state = app->dfu_state;
  frame->ble_paired = app->ble_paired != 0;

  if (bmi270_sample(&d->imu, &imu) != RING_BUS_OK) {
    set_err(app, "imu_sample_fail");
    return -3;
  }
  frame->ax = imu.ax; frame->ay = imu.ay; frame->az = imu.az;
  frame->gx = imu.gx; frame->gy = imu.gy; frame->gz = imu.gz;
  frame->confidence = 0.5f + 0.5f * app->cal_conf;

  if (iqs7222a_read_state(&d->cap, &cap) != RING_BUS_OK) {
    set_err(app, "cap_sample_fail");
    return -4;
  }
  frame->cap_flags = cap.touch_flags;
  frame->cap_touch = cap.touch;
  frame->cap_prox = cap.proximity;

  if (npm1300_read_status(&d->pmic, &batt) != RING_BUS_OK) {
    set_err(app, "pmic_sample_fail");
    return -5;
  }
  frame->vbat_mv = batt.vbat_mv;
  frame->batt_pct = batt.soc_pct;
  app->batt_pct = batt.soc_pct;
  frame->low_battery = batt.soc_pct < 15;

  if (se050_read_identity(&d->se, &ident) != RING_BUS_OK) return -6;
  memcpy(frame->se_uid, ident.device_uid, 16);
  for (int i = 0; i < 16; i++) challenge[i] = (uint8_t)(0xA0 + i);
  if (se050_auth_challenge(&d->se, challenge, response) != RING_BUS_OK) return -7;
  frame->se_auth_ok = true;

  dw3000_range(&d->uwb, &rng);
  frame->uwb_range_mm = rng.range_mm;
  frame->uwb_ok = rng.ranging_ok;

  bmm350_sample(&d->mag, &mag);
  frame->mx = mag.mx; frame->my = mag.my; frame->mz = mag.mz;

  mint_mac(app->key, frame->seq, ts_ms, frame->mac);
  frame->health = 0;
  if (frame->low_battery) frame->health |= 0x01;
  if (!frame->ble_paired) frame->health |= 0x02;
  if (app->cal_conf < 0.5f) frame->health |= 0x04;
  if (frame->dfu_state) frame->health |= 0x08;
  return 0;
}

int ring_app_health_telemetry(ring_app_t *app, char *buf, size_t n) {
  if (!app || !buf || !n) return -1;
  snprintf(buf, n,
           "{\"batt\":%u,\"cal\":%.2f,\"dfu\":%u,\"ble\":%d,\"imu\":%d,\"cap\":%d,"
           "\"se\":%d,\"pmic\":%d,\"uwb\":%d,\"mag\":%d,\"err\":\"%s\"}",
           app->batt_pct, (double)app->cal_conf, app->dfu_state, app->ble_paired,
           app->imu_ok, app->cap_ok, app->se_ok, app->pmic_ok, app->uwb_ok,
           app->mag_ok, app->last_error[0] ? app->last_error : "");
  return 0;
}
