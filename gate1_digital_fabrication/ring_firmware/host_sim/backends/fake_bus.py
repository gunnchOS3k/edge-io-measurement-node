#!/usr/bin/env python3
"""Fake I2C/SPI backends mirroring portable ring drivers (Continuation VI)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple


class BusError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass
class FakeI2C:
    mode: str = "healthy"  # healthy|init_fail_imu|invalid_sensor|low_battery|packet_loss|reconnect
    _regs: Dict[Tuple[int, int], int] = field(default_factory=dict)
    nacked: set = field(default_factory=set)
    xfer_count: int = 0
    connected: bool = True
    inject_loss: bool = False

    def __post_init__(self) -> None:
        self.reset_devices()

    def reset_devices(self) -> None:
        self._regs = {
            (0x68, 0x00): 0x24,  # BMI270 CHIP_ID
            (0x44, 0x00): 0x42,  # IQS7222A prod
            (0x44, 0x10): 0x01,
            (0x44, 0x11): 0x03,
            (0x48, 0xA5): 0x5E,  # SE050 ATR
            (0x6B, 0x7F): 0x13,  # npm1300 mark
            (0x6B, 0x10): 0x0F,  # VBAT MSB ~3900
            (0x6B, 0x11): 0x3C,  # VBAT LSB
            (0x6B, 0x02): 0x01,
            (0x14, 0x00): 0x33,  # BMM350
        }
        if self.mode == "invalid_sensor":
            self._regs[(0x68, 0x00)] = 0xFF
        if self.mode == "low_battery":
            self._regs[(0x6B, 0x10)] = 0x0D  # 3350
            self._regs[(0x6B, 0x11)] = 0x16
        if self.mode == "init_fail_imu":
            self.nacked.add(0x68)

    def write_read(self, addr7: int, w: bytes, rn: int) -> bytes:
        if not self.connected:
            raise BusError("reconnect_needed")
        self.xfer_count += 1
        if self.mode == "packet_loss" and self.inject_loss and self.xfer_count % 3 == 0:
            raise BusError("packet_loss")
        if addr7 in self.nacked:
            raise BusError("nack")
        if not w:
            raise BusError("inval")
        reg = w[0]
        out = bytearray(rn)
        if addr7 == 0x48 and reg == 0xA5 and rn >= 24:
            out[0] = 0x5E
            for i in range(1, 8):
                out[i] = 0x10 + i
            for i in range(8, 24):
                out[i] = 0xE0 + (i - 8)
            return bytes(out)
        if (addr7, reg) in self._regs and rn:
            out[0] = self._regs[(addr7, reg)]
        if addr7 == 0x68 and reg == 0x0C and rn >= 6:
            out[5] = 0x10  # ~1g az
        return bytes(out)

    def write(self, addr7: int, w: bytes) -> None:
        if not self.connected:
            raise BusError("reconnect_needed")
        if addr7 in self.nacked:
            raise BusError("nack")


@dataclass
class FakeSPI:
    populated: bool = False

    def xfer(self, cs_id: int, tx: bytes) -> bytes:
        if not self.populated:
            return bytes(len(tx))
        rx = bytearray(len(tx))
        if tx and tx[0] == 0x00 and len(tx) >= 2:
            rx[1] = 0xDE
        if tx and tx[0] == 0x01 and len(tx) >= 5:
            rx[1], rx[2] = 0xE8, 0x03
        return bytes(rx)
