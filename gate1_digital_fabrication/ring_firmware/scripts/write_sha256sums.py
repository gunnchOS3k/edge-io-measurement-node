#!/usr/bin/env python3
"""Write SHA256SUMS + size lines for ring firmware artifacts."""
from __future__ import annotations

import hashlib
from pathlib import Path

OUT = Path("build/out")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    names: list[Path] = []
    for pat in (
        "ring_firmware_*.elf",
        "ring_firmware_*.bin",
        "ring_firmware_*.hex",
        "ring_firmware_*.map",
        "slot0_image_signed_dev.bin",
        "MCUBOOT_SIGN_REPORT.json",
        "MCUBOOT_PIPELINE_REPORT.json",
        "ZEPHYR_WEST_PROBE.json",
        "STATIC_ANALYSIS_REPORT.json",
        "STATUS.json",
    ):
        names.extend(sorted(OUT.glob(pat)))
    pipe = OUT / "mcuboot_pipeline"
    if pipe.is_dir():
        names.extend(sorted(pipe.glob("*.bin")))
        names.extend(sorted(pipe.glob("*.json")))
    for extra in ("VERSION.txt", "ring_firmware_dev_host.elf"):
        p = OUT / extra
        if p.exists():
            names.append(p)
    seen: set[str] = set()
    lines: list[str] = []
    for f in names:
        if not f.exists() or f.name in seen:
            continue
        seen.add(f.name)
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        lines.append(f"{h}  {f.name}")
        if f.suffix == ".bin":
            print(f"SIZE {f.name} {f.stat().st_size}")
    (OUT / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("SHA256SUMS_OK")
    print("ARTIFACTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
