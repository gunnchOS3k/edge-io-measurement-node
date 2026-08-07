#!/usr/bin/env python3.11
from __future__ import annotations
import struct, sys, hashlib
from pathlib import Path

def read_progbits(path: Path):
    data = path.read_bytes()
    assert data[:4] == b"\x7fELF" and data[4] == 1
    e_shoff = struct.unpack_from("<I", data, 32)[0]
    e_shentsize = struct.unpack_from("<H", data, 46)[0]
    e_shnum = struct.unpack_from("<H", data, 48)[0]
    e_shstrndx = struct.unpack_from("<H", data, 50)[0]
    def sh(i):
        return struct.unpack_from("<IIIIIIIIII", data, e_shoff + i * e_shentsize)
    str_off = sh(e_shstrndx)[4]
    out = {}
    for i in range(e_shnum):
        name_off, sh_type, flags, addr, offset, size, *_ = sh(i)
        end = data.find(b"\0", str_off + name_off)
        name = data[str_off + name_off:end].decode()
        if sh_type == 1 and size > 0:
            out[name] = data[offset:offset+size]
    return out

def build_exec(text: bytes, flash_base=0):
    e_entry = (flash_base + 4) | 1
    phoff = 52
    payload_off = 84
    eh = bytearray(52)
    eh[0:4]=b"\x7fELF"; eh[4]=1; eh[5]=1; eh[6]=1
    struct.pack_into("<HHI", eh, 16, 2, 40, 1)
    struct.pack_into("<III", eh, 24, e_entry, phoff, 0)
    struct.pack_into("<IHHHHHH", eh, 36, 0, 52, 32, 1, 0, 0, 0)
    ph = bytearray(32)
    struct.pack_into("<IIIIIIII", ph, 0, 1, payload_off, flash_base, flash_base, len(text), len(text), 5, 4)
    return bytes(eh)+bytes(ph)+bytes(text)

def to_ihex(blob: bytes):
    lines=[]
    for i in range(0,len(blob),16):
        chunk=blob[i:i+16]; addr=i&0xFFFF; n=len(chunk)
        hs=f"{n:02X}{addr:04X}00"+chunk.hex().upper()
        csum=(n+(addr>>8)+(addr&0xFF)+sum(chunk))&0xFF
        csum=(~csum+1)&0xFF
        lines.append(":"+hs+f"{csum:02X}")
    lines.append(":00000001FF")
    return "\n".join(lines)+"\n"

def main():
    objs=[Path(p) for p in sys.argv[1:-1]]; out=Path(sys.argv[-1]); out.mkdir(parents=True, exist_ok=True)
    text=bytearray(); maps=[]
    order=(".isr_vector",".text",".text.startup",".rodata",".rodata.str1.1")
    for o in objs:
        secs=read_progbits(o)
        for name in order:
            if name in secs:
                while len(text)%4: text.append(0)
                maps.append(f"0x{len(text):08X} {len(secs[name]):6d} {o.name}:{name}")
                text += secs[name]
        for name,blob in secs.items():
            if name.startswith(".text") and name not in order:
                while len(text)%4: text.append(0)
                maps.append(f"0x{len(text):08X} {len(blob):6d} {o.name}:{name}")
                text += blob
    if not text: raise SystemExit("empty")
    elf=build_exec(bytes(text))
    (out/"ring_firmware_dev.elf").write_bytes(elf)
    (out/"ring_firmware_dev.bin").write_bytes(bytes(text))
    (out/"ring_firmware_dev.hex").write_text(to_ihex(bytes(text)))
    (out/"ring_firmware_dev.map").write_text("\n".join(maps)+f"\nTOTAL {len(text)}\n")
    print("packed", len(text), "bytes")
main()
