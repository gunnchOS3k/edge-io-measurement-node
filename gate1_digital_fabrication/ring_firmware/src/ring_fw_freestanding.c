#include "ring_fw_fs.h"

static float cal_conf = 0.0f;
static uint8_t batt_pct = 100;
static int low_power = 0;
static int ble_state = 0;

static int mcmp(const uint8_t *a, const uint8_t *b, size_t n) {
  for (size_t i=0;i<n;i++) if (a[i]!=b[i]) return 1; return 0;
}
static void mcpy(uint8_t *d, const uint8_t *s, size_t n) {
  for (size_t i=0;i<n;i++) d[i]=s[i];
}

static void simple_mac(const uint8_t key[16], uint32_t seq, uint32_t nonce, uint8_t out[16]) {
  for (int i=0;i<16;i++) out[i] = (uint8_t)(key[i] ^ (seq + i*13) ^ (nonce >> (i%8)) ^ 0xA5);
}

void ring_boot(ring_identity_t *id) {
  if (!id) return; id->boot_count += 1; id->seq = 1; cal_conf = 0; low_power = 0;
}
void ring_auth_mint(ring_auth_frame_t *out, uint32_t seq, uint32_t nonce, const uint8_t key[16]) {
  out->seq = seq; out->nonce = nonce; simple_mac(key, seq, nonce, out->mac);
}
bool ring_auth_verify(const ring_auth_frame_t *frame, uint32_t expected_seq, const uint8_t key[16]) {
  if (!frame || frame->seq != expected_seq) return false;
  uint8_t mac[16]; simple_mac(key, frame->seq, frame->nonce, mac);
  return mcmp(mac, frame->mac, 16)==0;
}
void ring_imu_filter(const ring_imu_sample_t *in, ring_imu_sample_t *out) {
  const float a = 0.2f; static ring_imu_sample_t s;
  s.ax = s.ax + a*(in->ax - s.ax); s.ay = s.ay + a*(in->ay - s.ay); s.az = s.az + a*(in->az - s.az);
  s.gx = s.gx + a*(in->gx - s.gx); s.gy = s.gy + a*(in->gy - s.gy); s.gz = s.gz + a*(in->gz - s.gz);
  s.confidence = in->confidence; *out = s;
}
int ring_gesture_extract(const ring_imu_sample_t *s) {
  if (!s) return 0;
  float m = s->ax*s->ax + s->ay*s->ay + s->az*s->az;
  if (m > 2.5f) return 1; if (s->gz > 1.5f) return 2; return 0;
}
void ring_calibration_reset(void) { cal_conf = 0.0f; }
float ring_calibration_confidence(void) { return cal_conf; }
void ring_battery_update(uint16_t mv, int8_t celsius) {
  (void)celsius;
  if (mv >= 4100) batt_pct = 100; else if (mv <= 3300) batt_pct = 0;
  else batt_pct = (uint8_t)((mv - 3300) * 100 / 800);
}
uint8_t ring_battery_pct(void) { return batt_pct; }
void ring_enter_low_power(void) { low_power = 1; }
void ring_haptic_pulse(uint8_t strength) { (void)strength; }
int ring_dfu_validate_header(const uint8_t *hdr, size_t n) {
  if (n < 8) return -1;
  return (hdr[0]=='D' && hdr[1]=='F' && hdr[2]=='U' && hdr[3]=='1') ? 0 : -2;
}
void ring_diag_emit(char *buf, size_t n) {
  const char *s="ring_fw_dev"; size_t i=0; if(!buf||!n) return;
  for(;s[i]&&i+1<n;i++) buf[i]=s[i]; buf[i]=0;
}
void ring_identity_set(ring_identity_t *id, const uint8_t device_id[16]) {
  if (id && device_id) mcpy(id->device_id, device_id, 16);
}
int ring_ble_pair_step(int cmd, const uint8_t *nonce16, uint8_t *resp16) {
  if (cmd == 1 && ble_state == 0) { ble_state = 1; return 1; }
  if (cmd == 2 && ble_state == 1 && nonce16 && resp16) {
    for (int i=0;i<16;i++) resp16[i] = (uint8_t)(nonce16[i] ^ 0x5A); ble_state = 2; return 2;
  }
  if (cmd == 3 && ble_state == 2) { ble_state = 3; return 3; }
  if (cmd == 4 && ble_state == 3) { ble_state = 4; return 4; }
  return ble_state == 4 ? 4 : -1;
}
int ring_ble_paired(void) { return ble_state == 4; }
void ring_telemetry_emit(char *buf, size_t n) {
  const char *s="telem"; size_t i=0; if(!buf||!n) return;
  for(;s[i]&&i+1<n;i++) buf[i]=s[i]; buf[i]=0;
}
int ring_factory_selftest(void) {
  uint8_t key[16]; for(int i=0;i<16;i++) key[i]=1;
  ring_auth_frame_t fr; ring_auth_mint(&fr,1,2,key);
  if (!ring_auth_verify(&fr,1,key)) return -1;
  uint8_t hdr[8]={'D','F','U','1',0,0,0,1};
  return ring_dfu_validate_header(hdr,8)==0 ? 0 : -2;
}
