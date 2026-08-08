#include "ring_fw.h"
#include "../app/ring_app.h"
#include "../drivers/bus/ring_bus_fake.h"
#include <stdio.h>
#include <string.h>

int main(void) {
  ring_fake_bus_t fb;
  ring_app_t app;
  ring_app_cfg_t cfg;
  ring_fusion_frame_t frame;
  char diag[256];
  char telem[256];
  uint8_t key[16];

  for (int i = 0; i < 16; i++) key[i] = (uint8_t)i;
  ring_fake_bus_init(&fb, RING_FAKE_MODE_HEALTHY);
  memset(&cfg, 0, sizeof cfg);
  cfg.i2c = &fb.i2c;
  cfg.spi = &fb.spi;
  cfg.uwb_populated = false;
  cfg.mag_enabled = false;
  cfg.session_key = key;

  if (ring_app_init(&app, &cfg) != 0) {
    fprintf(stderr, "init_fail %s\n", ring_app_last_error(&app));
    return 2;
  }
  ring_app_boot_diagnostics(&app, diag, sizeof diag);
  puts(diag);
  ring_app_ble_pair(&app);
  for (int i = 0; i < 4; i++) ring_app_calibrate_step(&app);
  ring_app_set_dfu_state(&app, 0);
  if (ring_app_tick(&app, 1000, &frame) != 0) return 3;
  ring_app_health_telemetry(&app, telem, sizeof telem);
  puts(telem);
  printf("fusion seq=%u batt=%u touch=%d conf=%.2f\n",
         frame.seq, frame.batt_pct, frame.cap_touch, frame.confidence);

  /* legacy protocol path still exercised */
  ring_identity_t id; memset(&id, 0, sizeof id);
  ring_boot(&id);
  puts("RING_FW_HOST_BUILD_OK development full_app");
  return 0;
}
