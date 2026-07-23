# Privacy and Body Data Boundary

## Classification

Body-area data is classified as **sensitive** in all contexts within this research. This includes:

- **Motion data**: Accelerometer, gyroscope, magnetometer readings from body-worn sensors
- **Biometric-like signals**: Heart rate, skin conductance, respiration patterns, or any physiological proxy
- **Environmental sensing near body**: Temperature, humidity, pressure, and ambient light when collected from a body-worn device
- **Location and positioning**: GPS, UWB ranging, BLE proximity, or any signal that can infer user location

## Ethics Review Requirement

**Ethics review is required** before any human participant data is collected, processed, or stored. This applies to:

- Any sensor data collected from a device worn by or near a human
- Any data that could identify, profile, or track an individual
- Any experimental protocol involving human subjects

No exceptions. Ethics approval must be obtained from the relevant institutional review board before data collection begins.

## Data Minimization

All data collection follows the principle of **data minimization**:

- Collect only the data necessary for the specific research evaluation
- Reduce precision where full resolution is not required
- Aggregate data when individual samples are not needed
- Delete raw data as soon as processed results are obtained
- Never collect data "in case it might be useful later"

## Local Processing Preference

Processing body-area data **locally on the device** is the default and preferred approach:

- Sensor data should be processed at the edge before any transmission
- Only derived results (not raw sensor streams) should be transmitted when possible
- Cloud or server-side processing of raw body-area data requires additional justification
- Local processing reduces exposure surface and supports privacy-by-design

## Consent Requirement

**No collection without informed consent.** Any human participant must:

- Be informed of what data is collected, how it is processed, and how long it is retained
- Provide explicit consent before any data collection begins
- Have the ability to withdraw consent and request data deletion at any time
- Understand any risks associated with body-area data collection

## Research Evaluation Fallback

For all research evaluation in this repository, the default approach uses **synthetic sensor traces**:

- Synthetic IMU streams with realistic noise profiles
- Replayed sensor recordings from public datasets (with appropriate licensing)
- Modeled biometric-like signals generated from physiological models
- Emulated environmental data based on published environmental parameters

This simulation path is sufficient for evaluating service-continuity methods, latency budgets, and energy performance without requiring human participant data.

## Summary

| Principle | Requirement |
|---|---|
| Classification | Body-area data is sensitive |
| Ethics review | Required for any human data |
| Data minimization | Collect only what is necessary |
| Processing location | Local/on-device preferred |
| Consent | Mandatory, informed, revocable |
| Default evaluation | Synthetic sensor traces |
