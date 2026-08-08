/*
 * Edge I/O Ring — full digital fusion application (Continuation VI).
 * DEVELOPMENT only. PHYSICAL_EXECUTION_FREEZE: not flashed to physical ring.
 */
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <string.h>
#include "ring_app.h"
#include "drivers/bus/ring_bus_fake.h"

#ifndef RING_FEATURE_UWB
#define RING_FEATURE_UWB 0
#endif
#ifndef RING_FEATURE_MAG
#define RING_FEATURE_MAG 0
#endif

int main(void)
{
	ring_fake_bus_t fb;
	ring_app_t app;
	ring_app_cfg_t cfg;
	ring_fusion_frame_t frame;
	char diag[192];
	char telem[192];
	uint8_t key[16];
	uint64_t ts = 0;

	for (int i = 0; i < 16; i++) {
		key[i] = (uint8_t)i;
	}

	ring_fake_bus_init(&fb, RING_FAKE_MODE_HEALTHY);
	memset(&cfg, 0, sizeof(cfg));
	cfg.i2c = &fb.i2c;
	cfg.spi = &fb.spi;
	cfg.uwb_populated = RING_FEATURE_UWB;
	cfg.mag_enabled = RING_FEATURE_MAG;
	cfg.session_key = key;

	printk("edge_io_ring full firmware digital boot\n");
	if (ring_app_init(&app, &cfg) != 0) {
		printk("sensor_init_fail %s\n", ring_app_last_error(&app));
		return 1;
	}
	ring_app_boot_diagnostics(&app, diag, sizeof(diag));
	printk("%s\n", diag);
	ring_app_ble_pair(&app);
	for (int i = 0; i < 4; i++) {
		ring_app_calibrate_step(&app);
	}

	while (1) {
		ts += 50;
		if (ring_app_tick(&app, ts, &frame) == 0) {
			ring_app_health_telemetry(&app, telem, sizeof(telem));
			printk("fusion seq=%u batt=%u touch=%d health=0x%02x\n",
			       frame.seq, frame.batt_pct, frame.cap_touch, frame.health);
			printk("%s\n", telem);
		}
		k_msleep(1000);
	}
	return 0;
}
