#!/usr/bin/env python3
"""MCUboot-like DEVELOPMENT image signing (HMAC-SHA256 envelope).

Compatibility wrapper — full sign/update/revert/factory/anti-replay lives in
mcuboot_dev_pipeline.py. DEVELOPMENT keys only. No physical boot claim.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load_pipeline():
    path = ROOT / "scripts" / "mcuboot_dev_pipeline.py"
    spec = importlib.util.spec_from_file_location("mcuboot_dev_pipeline", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", default=str(ROOT / "build/out/ring_firmware_release_development.bin"))
    ap.add_argument("--key", default=str(ROOT / "mcuboot/dev_keys/development.key"))
    ap.add_argument("--out", default=str(ROOT / "build/out"))
    args = ap.parse_args()
    pipe = _load_pipeline()
    bin_path = pathlib.Path(args.bin)
    if not bin_path.exists():
        alt = ROOT / "build/out/ring_firmware_dev.bin"
        if alt.exists():
            bin_path = alt
    meta = pipe.build_pipeline(bin_path, pathlib.Path(args.key), pathlib.Path(args.out))
    print("MCUBOOT_DEVELOPMENT_SIGN_PASS")
    print("RING_MCUBOOT_DEV_PIPELINE_PASS")
    print("RING_PHYSICAL_BOOT_PENDING")
    print(
        "MCUBOOT_DEV_SIGN_OK",
        json.dumps({k: meta[k] for k in ("signed", "verify_positive", "key_class")}),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
