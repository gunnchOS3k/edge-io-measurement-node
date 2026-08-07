#pragma once
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define RING_FW_VERSION_MAJOR 0
#define RING_FW_VERSION_MINOR 1
#define RING_FW_VERSION_PATCH 0
#define RING_FW_LABEL "development"

typedef struct {
  uint8_t device_id[16];
  uint32_t boot_count;
  uint32_t seq;
} ring_identity_t;

typedef struct {
  uint32_t nonce;
  uint32_t seq;
  uint8_t mac[16];
} ring_auth_frame_t;

typedef struct {
  float ax, ay, az, gx, gy, gz;
  float confidence;
} ring_imu_sample_t;

void ring_boot(ring_identity_t *id);
bool ring_auth_verify(const ring_auth_frame_t *frame, uint32_t expected_seq, const uint8_t key[16]);
void ring_auth_mint(ring_auth_frame_t *out, uint32_t seq, uint32_t nonce, const uint8_t key[16]);
void ring_imu_filter(const ring_imu_sample_t *in, ring_imu_sample_t *out);
int ring_gesture_extract(const ring_imu_sample_t *s);
void ring_calibration_reset(void);
float ring_calibration_confidence(void);
void ring_battery_update(uint16_t mv, int8_t celsius);
uint8_t ring_battery_pct(void);
void ring_enter_low_power(void);
void ring_haptic_pulse(uint8_t strength);
int ring_dfu_validate_header(const uint8_t *hdr, size_t n);
void ring_diag_emit(char *buf, size_t n);
