#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "ring_types.h"

ring_boot_mode_t ring_boot_init(uint32_t);
const char *ring_fw_version(void);
void ring_identity_init(const uint8_t*);
int ring_identity_get(uint8_t out[16]);
int ring_ble_pairing_step(int, const uint8_t*, uint8_t*);
int ring_ble_is_paired(void);
void ring_auth_reset(void);
int ring_auth_sign(const uint8_t*, ring_auth_event_t*);
int ring_auth_verify_and_accept(const uint8_t*, const ring_auth_event_t*);
int ring_sensors_init(void);
int ring_sensors_read(imu_sample_t*);
void ring_fusion_reset(void);
void ring_fusion_update(const imu_sample_t*, float, float*);
int ring_gesture_classify(const float*, float);
int ring_calib_start(void);
int ring_battery_pct(void);
void ring_battery_set_mv(uint16_t);
int ring_haptics_play(int);
int ring_dfu_begin(uint32_t);
int ring_factory_selftest(void);
int ring_low_power_enter(void);
int ring_low_power_is_sleeping(void);

static int fails;

#define EXPECT(c) do { if (!(c)) { printf("FAIL %s:%d\n", __FILE__, __LINE__); fails++; } } while(0)

int main(void) {
  EXPECT(ring_boot_init(0) == RING_BOOT_COLD);
  EXPECT(strcmp(ring_fw_version(), "0.1.0-dev") == 0);
  ring_identity_init(0);
  uint8_t id[16]; EXPECT(ring_identity_get(id) == 0);
  uint8_t nonce[16]={1}, resp[16];
  EXPECT(ring_ble_pairing_step(1,0,0)==1);
  EXPECT(ring_ble_pairing_step(2,nonce,resp)==2);
  EXPECT(ring_ble_pairing_step(3,0,0)==3);
  EXPECT(ring_ble_pairing_step(4,0,0)==4);
  EXPECT(ring_ble_is_paired()==1);
  ring_auth_reset();
  uint8_t key[16]={9};
  ring_auth_event_t ev; memset(&ev,0,sizeof ev); ev.seq=1; ev.event_type=1;
  ring_auth_sign(key,&ev);
  EXPECT(ring_auth_verify_and_accept(key,&ev)==0);
  EXPECT(ring_auth_verify_and_accept(key,&ev)==-3); /* replay */
  EXPECT(ring_sensors_init()==0);
  imu_sample_t s; EXPECT(ring_sensors_read(&s)==0);
  ring_fusion_reset(); float o[3]; ring_fusion_update(&s,0.5f,o);
  float acc[3]={0,0,1}; EXPECT(ring_gesture_classify(acc,0.5f)!=0);
  EXPECT(ring_calib_start()==0);
  ring_battery_set_mv(3900); EXPECT(ring_battery_pct()>0);
  EXPECT(ring_haptics_play(1)==0);
  EXPECT(ring_dfu_begin(1024)==0);
  EXPECT(ring_factory_selftest()==0);
  EXPECT(ring_low_power_enter()==0);
  EXPECT(ring_low_power_is_sleeping()==1);
  if (fails) { printf("%d failures\n", fails); return 1; }
  printf("OK unit tests passed (development firmware)\n");
  return 0;
}
