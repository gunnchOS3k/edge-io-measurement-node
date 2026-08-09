"""Sibling import helpers for authenticated_ring_input + gunnchOS ring_input."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


def repos_root() -> Path:
    # .../repos/edge-io-measurement-node/src/edge_io_node/ring_e2e/siblings.py
    return Path(__file__).resolve().parents[4]


def load_authenticated_ring_input():
    candidates = [
        repos_root() / "gunnchos-hardware-industrial-design" / "ring_input" / "python",
        Path(
            "/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/"
            "gunnchos-hardware-industrial-design/ring_input/python"
        ),
    ]
    for root in candidates:
        if (root / "authenticated_ring_input" / "__init__.py").exists():
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))
            return importlib.import_module("authenticated_ring_input")
    raise ImportError("authenticated_ring_input sibling package not found")


def load_gunnchos_ring_adapter():
    candidates = [
        repos_root() / "gunnchos-device-os",
        Path(
            "/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/"
            "gunnchos-device-os"
        ),
    ]
    for root in candidates:
        if (root / "ring_input" / "adapter.py").exists():
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))
            return importlib.import_module("ring_input")
    raise ImportError("gunnchos-device-os/ring_input not found")


def firmware_host_sim() -> Any:
    """Load Continuation VI/VII host fusion simulator (fake buses → events)."""
    fw = (
        Path(__file__).resolve().parents[3]
        / "gate1_digital_fabrication"
        / "ring_firmware"
        / "host_sim"
    )
    # parents[3] from ring_e2e = edge-io repo root? 
    # ring_e2e -> edge_io_node -> src -> repo  => parents[3]
    if not (fw / "ring_host_sim.py").exists():
        fw = repos_root() / "edge-io-measurement-node" / "gate1_digital_fabrication" / "ring_firmware" / "host_sim"
    if str(fw) not in sys.path:
        sys.path.insert(0, str(fw))
    return importlib.import_module("ring_host_sim")
