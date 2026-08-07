#include "ring_fw.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>

int main(void) {
  uint8_t key[16]={0}; for(int i=0;i<16;i++) key[i]=(uint8_t)(i*3);
  ring_auth_frame_t fr; ring_auth_mint(&fr, 5, 99, key);
  assert(ring_auth_verify(&fr, 5, key));
  assert(!ring_auth_verify(&fr, 6, key)); /* anti-replay seq mismatch */
  ring_auth_frame_t bad=fr; bad.mac[0]^=0xff;
  assert(!ring_auth_verify(&bad, 5, key));
  uint8_t hdr[8]={'D','F','U','1',0,0,0,1};
  assert(ring_dfu_validate_header(hdr,8)==0);
  assert(ring_dfu_validate_header((uint8_t*)"XXXX",4)<0);
  ring_calibration_reset();
  assert(ring_calibration_confidence()==0.0f);
  puts("TEST_RING_FW_PASS");
  return 0;
}
