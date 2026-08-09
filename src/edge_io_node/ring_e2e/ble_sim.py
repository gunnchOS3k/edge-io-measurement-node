"""BLE transport simulator between ring firmware and gunnchOS ring service."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BleTransportSim:
    connected: bool = True
    mtu: int = 247
    tx_queue: list[dict[str, Any]] = field(default_factory=list)
    rx_queue: list[dict[str, Any]] = field(default_factory=list)
    drops: int = 0
    reconnects: int = 0

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def lose_link(self) -> None:
        self.connected = False

    def reconnect(self) -> None:
        self.connected = True
        self.reconnects += 1

    def send(self, packet: dict[str, Any]) -> bool:
        if not self.connected:
            self.drops += 1
            return False
        self.tx_queue.append(dict(packet))
        self.rx_queue.append(dict(packet))
        return True

    def recv(self) -> dict[str, Any] | None:
        if not self.rx_queue:
            return None
        return self.rx_queue.pop(0)
