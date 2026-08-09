/* SPDX-License-Identifier: Apache-2.0 */
/* Continuation VII — driver depth host proof. */
#include "../app/ring_app.h"
#include "../drivers/bus/ring_bus_fake.h"
#include "../drivers/bmi270/bmi270.h"
#include "../drivers/iqs7222a/iqs7222a.h"
#include "../drivers/se050/se050.h"
#include "../drivers/npm1300/npm1300.h"
#include "../drivers/dw3000/dw3000.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

int main(void) {
  ring_fake_bus_t fb;
  bmi270_dev_t imu;
  iqs7222a_dev_t cap;
  se050_dev_t se;
  npm1300_dev_t pmic;
  dw3000_dev_t uwb;
  bmi270_diag_t id;
  iqs7222a_diag_t cd;
  se050_diag_t sd;
  npm1300_diag_t nd;
  dw3000_diag_t ud;
  bmi270_sample_t sample;
  iqs7222a_state_t st;
  npm1300_status_t batt;
  dw3000_range_t rng;
  uint8_t ch[16], resp[16];

  ring_fake_bus_init(&fb, RING_FAKE_MODE_HEALTHY);

  assert(bmi270_init(&imu, &fb.i2c, 0) == RING_BUS_OK);
  assert(bmi270_configure(&imu, BMI270_ACC_CONF_ODR100, BMI270_ACC_RANGE_8G,
                           BMI270_GYR_CONF_ODR100, BMI270_GYR_RANGE_2000) == RING_BUS_OK);
  assert(bmi270_sample(&imu, &sample) == RING_BUS_OK);
  assert(bmi270_diagnostics(&imu, &id) == RING_BUS_OK);
  assert(id.chip_id == BMI270_CHIP_ID_VALUE);
  assert(bmi270_recover(&imu) == RING_BUS_OK);

  assert(iqs7222a_init(&cap, &fb.i2c, 0) == RING_BUS_OK);
  assert(iqs7222a_read_state(&cap, &st) == RING_BUS_OK);
  assert(st.channel_count > 0);
  assert(iqs7222a_diagnostics(&cap, &cd) == RING_BUS_OK);
  assert(iqs7222a_recover(&cap) == RING_BUS_OK);

  assert(se050_init(&se, &fb.i2c, 0) == RING_BUS_OK);
  for (int i = 0; i < 16; i++) ch[i] = (uint8_t)(0xA0 + i);
  assert(se050_auth_challenge(&se, ch, resp) == RING_BUS_OK);
  assert(se050_diagnostics(&se, &sd) == RING_BUS_OK);
  assert(se050_recover(&se) == RING_BUS_OK);

  assert(npm1300_init(&pmic, &fb.i2c, 0) == RING_BUS_OK);
  assert(npm1300_read_status(&pmic, &batt) == RING_BUS_OK);
  assert(batt.vbat_mv > 0);
  assert(npm1300_diagnostics(&pmic, &nd) == RING_BUS_OK);
  assert(npm1300_recover(&pmic) == RING_BUS_OK);

  assert(dw3000_init(&uwb, &fb.spi, 0, true) == RING_BUS_OK);
  assert(dw3000_range(&uwb, &rng) == RING_BUS_OK);
  assert(rng.ranging_ok);
  assert(dw3000_diagnostics(&uwb, &ud) == RING_BUS_OK);
  assert(dw3000_recover(&uwb) == RING_BUS_OK);

  /* DNP path still compile-clean */
  assert(dw3000_init(&uwb, &fb.spi, 0, false) == RING_BUS_OK);
  assert(dw3000_range(&uwb, &rng) == RING_BUS_OK);
  assert(!rng.ranging_ok);

  puts("driver_depth_ok");
  return 0;
}
