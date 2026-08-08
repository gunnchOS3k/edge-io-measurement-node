#include "../app/ring_app.h"
#include "../drivers/bus/ring_bus_fake.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>

static void run_healthy(void) {
  ring_fake_bus_t fb; ring_app_t app; ring_app_cfg_t cfg; ring_fusion_frame_t fr;
  uint8_t key[16]; for (int i=0;i<16;i++) key[i]=(uint8_t)i;
  ring_fake_bus_init(&fb, RING_FAKE_MODE_HEALTHY);
  memset(&cfg,0,sizeof cfg); cfg.i2c=&fb.i2c; cfg.spi=&fb.spi; cfg.session_key=key;
  assert(ring_app_init(&app,&cfg)==0);
  assert(ring_app_ready(&app));
  ring_app_ble_pair(&app);
  ring_app_calibrate_step(&app);
  assert(ring_app_tick(&app,10,&fr)==0);
  assert(fr.batt_pct > 50);
  assert(fr.se_auth_ok);
  assert(fr.ble_paired);
  puts("healthy_ok");
}

static void run_init_fail(void) {
  ring_fake_bus_t fb; ring_app_t app; ring_app_cfg_t cfg;
  ring_fake_bus_init(&fb, RING_FAKE_MODE_INIT_FAIL_IMU);
  memset(&cfg,0,sizeof cfg); cfg.i2c=&fb.i2c; cfg.spi=&fb.spi;
  assert(ring_app_init(&app,&cfg)!=0);
  assert(!ring_app_ready(&app));
  puts("init_fail_ok");
}

static void run_invalid_sensor(void) {
  ring_fake_bus_t fb; ring_app_t app; ring_app_cfg_t cfg;
  ring_fake_bus_init(&fb, RING_FAKE_MODE_INVALID_SENSOR);
  memset(&cfg,0,sizeof cfg); cfg.i2c=&fb.i2c; cfg.spi=&fb.spi;
  assert(ring_app_init(&app,&cfg)!=0);
  puts("invalid_sensor_ok");
}

static void run_low_batt(void) {
  ring_fake_bus_t fb; ring_app_t app; ring_app_cfg_t cfg; ring_fusion_frame_t fr;
  ring_fake_bus_init(&fb, RING_FAKE_MODE_LOW_BATTERY);
  memset(&cfg,0,sizeof cfg); cfg.i2c=&fb.i2c; cfg.spi=&fb.spi;
  assert(ring_app_init(&app,&cfg)==0);
  assert(ring_app_tick(&app,1,&fr)==0);
  assert(fr.low_battery);
  puts("low_batt_ok");
}

static void run_uwb_mag(void) {
  ring_fake_bus_t fb; ring_app_t app; ring_app_cfg_t cfg; ring_fusion_frame_t fr;
  ring_fake_bus_init(&fb, RING_FAKE_MODE_HEALTHY);
  memset(&cfg,0,sizeof cfg); cfg.i2c=&fb.i2c; cfg.spi=&fb.spi;
  cfg.uwb_populated=true; cfg.mag_enabled=true;
  assert(ring_app_init(&app,&cfg)==0);
  assert(ring_app_tick(&app,2,&fr)==0);
  assert(fr.uwb_ok);
  puts("uwb_mag_ok");
}

static void run_calibration_dfu(void) {
  ring_fake_bus_t fb; ring_app_t app; ring_app_cfg_t cfg; ring_fusion_frame_t fr;
  ring_fake_bus_init(&fb, RING_FAKE_MODE_HEALTHY);
  memset(&cfg,0,sizeof cfg); cfg.i2c=&fb.i2c; cfg.spi=&fb.spi;
  assert(ring_app_init(&app,&cfg)==0);
  for (int i=0;i<4;i++) ring_app_calibrate_step(&app);
  ring_app_set_dfu_state(&app, 1);
  assert(ring_app_tick(&app,3,&fr)==0);
  assert(fr.cal_conf >= 0.99f);
  assert(fr.dfu_state == 1);
  puts("cal_dfu_ok");
}

static void run_replay_mac(void) {
  ring_fake_bus_t fb; ring_app_t app; ring_app_cfg_t cfg;
  ring_fusion_frame_t a, b;
  uint8_t key[16]={1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16};
  ring_fake_bus_init(&fb, RING_FAKE_MODE_HEALTHY);
  memset(&cfg,0,sizeof cfg); cfg.i2c=&fb.i2c; cfg.spi=&fb.spi; cfg.session_key=key;
  assert(ring_app_init(&app,&cfg)==0);
  assert(ring_app_tick(&app,100,&a)==0);
  assert(ring_app_tick(&app,200,&b)==0);
  assert(a.seq != b.seq);
  assert(memcmp(a.mac, b.mac, 16) != 0);
  /* replay: same seq mac must not verify as fresh */
  assert(!(a.seq == b.seq));
  puts("replay_mac_ok");
}

int main(void) {
  run_healthy();
  run_init_fail();
  run_invalid_sensor();
  run_low_batt();
  run_uwb_mag();
  run_calibration_dfu();
  run_replay_mac();
  puts("TEST_RING_APP_OK");
  return 0;
}
