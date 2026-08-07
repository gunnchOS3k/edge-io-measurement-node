#!/usr/bin/env python3
"""Host simulator for Edge I/O Ring protocol (nonphysical)."""
from __future__ import annotations
import hashlib, struct

def mint_frame(seq: int, nonce: int, key: bytes) -> bytes:
    mac = bytes((key[i] ^ ((seq + i*13) & 0xFF) ^ ((nonce >> (i%8)) & 0xFF) ^ 0xA5) for i in range(16))
    return struct.pack("<II", seq, nonce) + mac

def verify_frame(frame: bytes, expected_seq: int, key: bytes) -> bool:
    seq, nonce = struct.unpack_from("<II", frame, 0)
    if seq != expected_seq:
        return False
    return frame[8:24] == mint_frame(seq, nonce, key)[8:24]

if __name__ == "__main__":
    key = bytes(range(16))
    fr = mint_frame(1, 0x11, key)
    assert verify_frame(fr, 1, key)
    assert not verify_frame(fr, 2, key)
    print("HOST_SIM_PASS")
