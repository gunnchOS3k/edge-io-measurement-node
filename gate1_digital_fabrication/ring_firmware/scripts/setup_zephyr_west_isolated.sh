#!/usr/bin/env bash
# Isolated Zephyr/west toolchain bootstrap (no global pip pollution).
# Does NOT claim RING_ZEPHYR_WEST_BUILD_PASS — that requires a real west build.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TC="${ROOT}/.toolchain"
VENV="${TC}/west-venv"
PY="${PY:-python3.11}"

mkdir -p "${TC}"
if [[ ! -x "${VENV}/bin/west" ]]; then
  "${PY}" -m venv "${VENV}"
  "${VENV}/bin/pip" install --upgrade pip
  "${VENV}/bin/pip" install 'west>=1.2'
fi
"${VENV}/bin/west" --version | tee "${TC}/west-version.txt"
"${VENV}/bin/pip" freeze > "${TC}/west-venv-requirements.lock.txt"

cat > "${TC}/WEST_ISOLATED_ENV.json" <<EOF
{
  "venv": "${VENV}",
  "west_present": true,
  "zephyr_base": "${ZEPHYR_BASE:-}",
  "zephyr_sdk_install_dir": "${ZEPHYR_SDK_INSTALL_DIR:-}",
  "global_pip_pollution": false,
  "physical_boot_claimed": false,
  "note": "Isolated west venv only. Full SDK + west build are separate gates."
}
EOF

echo "WEST_ISOLATED_VENV_OK"
echo "RING_PHYSICAL_BOOT_PENDING"
