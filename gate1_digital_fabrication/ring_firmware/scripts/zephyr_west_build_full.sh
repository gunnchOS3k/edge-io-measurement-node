#!/usr/bin/env bash
# Build full fusion zephyr_app when SDK present. Soft-skip otherwise.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WEST_BIN="${ROOT}/.toolchain/west-venv/bin/west"
export PATH="${ROOT}/.toolchain/west-venv/bin:${PATH:-}"

if [[ -z "${ZEPHYR_BASE:-}" ]]; then
  for cand in "$HOME/zephyr-workspace/zephyr" "/Users/gunnchos/zephyr-workspace/zephyr"; do
    if [[ -d "$cand" ]]; then export ZEPHYR_BASE="$cand"; break; fi
  done
fi
if [[ -z "${ZEPHYR_SDK_INSTALL_DIR:-}" ]]; then
  for cand in "$HOME/zephyr-workspace/zephyr-sdk-0.16.8" "/Users/gunnchos/zephyr-workspace/zephyr-sdk-0.16.8"; do
    if [[ -d "$cand" ]]; then export ZEPHYR_SDK_INSTALL_DIR="$cand"; break; fi
  done
fi
export ZEPHYR_TOOLCHAIN_VARIANT="${ZEPHYR_TOOLCHAIN_VARIANT:-zephyr}"

if [[ ! -x "$WEST_BIN" ]] || [[ -z "${ZEPHYR_BASE:-}" ]] || [[ -z "${ZEPHYR_SDK_INSTALL_DIR:-}" ]]; then
  echo "ZEPHYR_WEST_BUILD_SOFT_SKIP (SDK/west incomplete)"
  exit 0
fi

# Prefer venv cmake if present (Homebrew CMake 4.x breaks Zephyr 3.7)
if [[ -x "${ROOT}/.toolchain/west-venv/bin/cmake" ]]; then
  export PATH="${ROOT}/.toolchain/west-venv/bin:$PATH"
fi

mkdir -p build/out/zephyr_west docs
BOARD="${RING_ZEPHYR_BOARD:-nrf52840dk/nrf52840}"

echo "west build board=$BOARD app=zephyr_app"
"$WEST_BIN" build -b "$BOARD" -d build/zephyr_west zephyr_app -- -DCMAKE_PREFIX_PATH="${ROOT}/.toolchain/west-venv" 2>&1 | tee docs/WEST_BUILD_LOG.txt

cp -f build/zephyr_west/zephyr/zephyr.elf build/out/zephyr_west/ring_zephyr_nrf52840.elf
cp -f build/zephyr_west/zephyr/zephyr.bin build/out/zephyr_west/ring_zephyr_nrf52840.bin 2>/dev/null || true
cp -f build/zephyr_west/zephyr/zephyr.hex build/out/zephyr_west/ring_zephyr_nrf52840.hex 2>/dev/null || true
(cd build/out/zephyr_west && shasum -a 256 ring_zephyr_nrf52840.* > SHA256SUMS)
python3 - <<'PY'
import json
from pathlib import Path
from datetime import datetime, timezone
probe = {
  "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "west_build_pass": True,
  "board": "nrf52840dk/nrf52840",
  "app": "zephyr_app full fusion",
  "blockers": [],
}
Path("build/out/ZEPHYR_WEST_PROBE.json").write_text(json.dumps(probe, indent=2)+"\n")
Path("docs/ZEPHYR_WEST_PROBE.json").write_text(json.dumps(probe, indent=2)+"\n")
print("RING_ZEPHYR_WEST_BUILD_PASS")
PY
