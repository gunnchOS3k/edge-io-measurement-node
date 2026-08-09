/*
 * Edge I/O Ring — Zephyr-native production application (Continuation VII).
 * PHYSICAL_EXECUTION_FREEZE: not flashed to physical ring.
 *
 * Primary path: DEVICE_DT_GET → Zephyr I2C/SPI → portable drivers → fusion → BLE.
 * CONFIG_RING_USE_FAKE_BUS=y keeps digital DK bring-up without on-board sensors.
 */
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/settings/settings.h>
#include <zephyr/pm/device.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/sys/printk.h>
#include <string.h>

#include "ring_app.h"
#include "drivers/bus/ring_bus_fake.h"
#include "drivers/bus/ring_bus_zephyr.h"

LOG_MODULE_REGISTER(edge_io_ring, LOG_LEVEL_INF);

#ifndef RING_FEATURE_UWB
#define RING_FEATURE_UWB 0
#endif
#ifndef RING_FEATURE_MAG
#define RING_FEATURE_MAG 0
#endif

#ifndef CONFIG_RING_USE_FAKE_BUS
#define CONFIG_RING_USE_FAKE_BUS 1
#endif

static uint8_t g_session_key[16];
static bool g_cal_persisted;

static int ring_settings_set(const char *name, size_t len,
                             settings_read_cb read_cb, void *cb_arg)
{
	const char *next;
	if (settings_name_steq(name, "cal_done", &next) && !next) {
		if (len != sizeof(g_cal_persisted)) return -EINVAL;
		if (read_cb(cb_arg, &g_cal_persisted, len) < 0) return -EIO;
		return 0;
	}
	return -ENOENT;
}

SETTINGS_STATIC_HANDLER_DEFINE(ring, "ring", NULL, ring_settings_set, NULL, NULL);

static void ring_ble_ready(int err)
{
	if (err) {
		LOG_ERR("bt_enable failed %d", err);
		return;
	}
	LOG_INF("BLE stack ready (digital)");
}

static int ring_pm_suspend(void)
{
#if DT_NODE_EXISTS(DT_NODELABEL(i2c0))
	const struct device *i2c = DEVICE_DT_GET(DT_NODELABEL(i2c0));
	if (device_is_ready(i2c)) {
		(void)pm_device_action_run(i2c, PM_DEVICE_ACTION_SUSPEND);
	}
#endif
	return 0;
}

int main(void)
{
	ring_app_t app;
	ring_app_cfg_t cfg;
	ring_fusion_frame_t frame;
	char diag[192];
	char telem[192];
	uint64_t ts = 0;
	int rc;

	for (int i = 0; i < 16; i++) {
		g_session_key[i] = (uint8_t)i;
	}

	LOG_INF("edge_io_ring Zephyr-native digital boot");
	(void)settings_subsys_init();
	(void)settings_load();
	(void)bt_enable(ring_ble_ready);

	memset(&cfg, 0, sizeof(cfg));
	cfg.uwb_populated = RING_FEATURE_UWB;
	cfg.mag_enabled = RING_FEATURE_MAG;
	cfg.session_key = g_session_key;

#if CONFIG_RING_USE_FAKE_BUS
	{
		static ring_fake_bus_t fb;
		ring_fake_bus_init(&fb, RING_FAKE_MODE_HEALTHY);
		cfg.i2c = &fb.i2c;
		cfg.spi = &fb.spi;
		LOG_WRN("CONFIG_RING_USE_FAKE_BUS=y — digital DK path (not EVT silicon)");
	}
#else
	{
		static ring_zephyr_bus_t zb;
		const struct device *i2c = DEVICE_DT_GET(DT_NODELABEL(i2c0));
#if DT_NODE_HAS_STATUS(DT_NODELABEL(spi0), okay)
		const struct device *spi = DEVICE_DT_GET(DT_NODELABEL(spi0));
#else
		const struct device *spi = NULL;
#endif
		if (!device_is_ready(i2c)) {
			LOG_ERR("i2c0 not ready");
			return 1;
		}
		rc = ring_zephyr_bus_bind(&zb, i2c, spi);
		if (rc != 0) {
			LOG_ERR("zephyr bus bind failed %d", rc);
			return 1;
		}
		cfg.i2c = &zb.i2c;
		cfg.spi = spi ? &zb.spi : NULL;
		LOG_INF("Zephyr DEVICE_DT_GET I2C/SPI bound");
	}
#endif

	if (ring_app_init(&app, &cfg) != 0) {
		LOG_ERR("sensor_init_fail %s", ring_app_last_error(&app));
		return 1;
	}
	ring_app_boot_diagnostics(&app, diag, sizeof(diag));
	LOG_INF("%s", diag);
	ring_app_ble_pair(&app);
	if (!g_cal_persisted) {
		for (int i = 0; i < 4; i++) {
			ring_app_calibrate_step(&app);
		}
		g_cal_persisted = true;
		(void)settings_save_one("ring/cal_done", &g_cal_persisted,
					sizeof(g_cal_persisted));
	}

	while (1) {
		ts += 50;
		if (ring_app_tick(&app, ts, &frame) == 0) {
			ring_app_health_telemetry(&app, telem, sizeof(telem));
			LOG_INF("fusion seq=%u batt=%u touch=%d health=0x%02x",
				frame.seq, frame.batt_pct, frame.cap_touch, frame.health);
			LOG_DBG("%s", telem);
		}
		if ((ts % 5000) == 0) {
			(void)ring_pm_suspend();
		}
		k_msleep(1000);
	}
	return 0;
}
