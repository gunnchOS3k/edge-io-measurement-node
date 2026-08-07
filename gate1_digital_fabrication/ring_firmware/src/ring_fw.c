#include "ring_fw.h"
#include <string.h>
#include <stdio.h>

static float cal_conf = 0.0f;
static uint8_t batt_pct = 100;
static int low_power = 0;

static void simple_mac(const uint8_t key[16], uint32_t seq, uint32_t nonce, uint8_t out[16]) {
  /* Development-only keyed hash stand-in (NOT production crypto). */
  for (int i=0;i<16;i++) {
    out[i] = (uint8_t)(key[i] ^ (seq + i*13) ^ (nonce >> (i%8)) ^ 0xA5);
  }
}

void ring_boot(ring_identity_t *id) {
  if (!id) return;
  id->boot_count += 1;
  id->seq = 1;
  cal_conf = 0.0f;
  low_power = 0;
}

void ring_auth_mint(ring_auth_frame_t *out, uint32_t seq, uint32_t nonce, const uint8_t key[16]) {
  out->seq = seq; out->nonce = nonce;
  simple_mac(key, seq, nonce, out->mac);
}

bool ring_auth_verify(const ring_auth_frame_t *frame, uint32_t expected_seq, const uint8_t key[16]) {
  if (!frame) return false;
  if (frame->seq != expected_seq) return false; /* anti-replay: exact seq for unit tests; production uses window */
  uint8_t mac[16];
  simple_mac(key, frame->seq, frame->nonce, mac);
  return memcmp(mac, frame->mac, 16) == 0;
}

void ring_imu_filter(const ring_imu_sample_t *in, ring_imu_sample_t *out) {
  /* Simple 1st-order low-pass stand-in */
  const float a = 0.2f;
  static ring_imu_sample_t s = {0};
  s.ax = s.ax + a*(in->ax - s.ax);
  s.ay = s.ay + a*(in->ay - s.ay);
  s.az = s.az + a*(in->az - s.az);
  s.gx = s.gx + a*(in->gx - s.gx);
  s.gy = s.gy + a*(in->gy - s.gy);
  s.gz = s.gz + a*(in->gz - s.gz);
  s.confidence = in->confidence;
  *out = s;
}

int ring_gesture_extract(const ring_imu_sample_t *s) {
  if (!s) return 0;
  float m = s->ax*s->ax + s->ay*s->ay + s->az*s->az;
  if (m > 2.5f) return 1; /* tap-ish */
  if (s->gz > 1.5f) return 2; /* twist */
  return 0;
}

void ring_calibration_reset(void) { cal_conf = 0.0f; }
float ring_calibration_confidence(void) { return cal_conf; }

void ring_battery_update(uint16_t mv, int8_t celsius) {
  (void)celsius;
  if (mv >= 4100) batt_pct = 100;
  else if (mv <= 3300) batt_pct = 0;
  else batt_pct = (uint8_t)((mv - 3300) * 100 / 800);
}

uint8_t ring_battery_pct(void) { return batt_pct; }
void ring_enter_low_power(void) { low_power = 1; }
void ring_haptic_pulse(uint8_t strength) { (void)strength; /* HW later */ }

int ring_dfu_validate_header(const uint8_t *hdr, size_t n) {
  if (n < 8) return -1;
  return (hdr[0]=='D' && hdr[1]=='F' && hdr[2]=='U' && hdr[3]=='1') ? 0 : -2;
}

void ring_diag_emit(char *buf, size_t n) {
  snprintf(buf, n, "ring_fw %d.%d.%d-%s batt=%u cal=%.2f lp=%d",
    RING_FW_VERSION_MAJOR, RING_FW_VERSION_MINOR, RING_FW_VERSION_PATCH,
    RING_FW_LABEL, batt_pct, cal_conf, low_power);
}
