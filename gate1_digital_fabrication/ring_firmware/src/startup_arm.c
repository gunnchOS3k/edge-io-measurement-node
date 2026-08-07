#include "ring_fw_fs.h"
void Reset_Handler(void) {
  ring_identity_t id;
  for (int i=0;i<16;i++) id.device_id[i]=(uint8_t)(0xA0+i);
  id.boot_count=0; id.seq=0;
  ring_boot(&id);
  for(;;) {}
}
void * const g_vectors[] __attribute__((section(".isr_vector"), used)) = {
  (void*)0x20004000, (void*)Reset_Handler,
};
