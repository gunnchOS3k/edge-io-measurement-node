#include "ring_fw.h"
#include <stdio.h>
#include <string.h>

int main(void) {
  ring_identity_t id; memset(&id, 0, sizeof id);
  for (int i=0;i<16;i++) id.device_id[i]=(uint8_t)(0x10+i);
  ring_boot(&id);
  uint8_t key[16]; for (int i=0;i<16;i++) key[i]=(uint8_t)i;
  ring_auth_frame_t fr; ring_auth_mint(&fr, 1, 0xABCD1234u, key);
  if (!ring_auth_verify(&fr, 1, key)) return 2;
  ring_imu_sample_t in={.ax=0.1f,.ay=0,.az=1.0f,.confidence=0.9f}, out;
  ring_imu_filter(&in,&out);
  ring_battery_update(3900, 28);
  char diag[128]; ring_diag_emit(diag, sizeof diag);
  puts(diag);
  puts("RING_FW_HOST_BUILD_OK development");
  return 0;
}
