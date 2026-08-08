# Vendor / upstream driver notes

- Zephyr BMI270 / npm1300: Apache-2.0 — register maps referenced; not copied wholesale.
- Azoteq IQS7222A: no Zephyr upstream; custom portable driver from public datasheet defaults.
- NXP SE050: full Plug&Trust middleware not vendored (size/license). Lite I2C identity/auth path only.
- Qorvo DW3000: custom DNP/populated SPI path; Zephyr ships DW1000 only.
