#!/usr/bin/env python3
"""Probe Zephyr/west readiness for digital closure.

Emits RING_ZEPHYR_WEST_BUILD_PASS only when a real west build can be proven.
Never claims physical boot.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TC = ROOT / ".toolchain"
OUT = ROOT / "build" / "out"
DOCS = ROOT / "docs"


def _west_bin() -> Path | None:
    cand = TC / "west-venv" / "bin" / "west"
    if cand.is_file():
        return cand
    which = shutil.which("west")
    return Path(which) if which else None


def probe() -> dict:
    west = _west_bin()
    zephyr_base = os.environ.get("ZEPHYR_BASE", "").strip()
    sdk = os.environ.get("ZEPHYR_SDK_INSTALL_DIR", "").strip()
    west_ver = None
    if west:
        try:
            west_ver = subprocess.check_output([str(west), "--version"], text=True).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            west_ver = f"error:{exc}"

    blockers: list[str] = []
    if not west:
        blockers.append("west binary absent (run scripts/setup_zephyr_west_isolated.sh)")
    if not zephyr_base or not Path(zephyr_base).is_dir():
        blockers.append(
            "ZEPHYR_BASE unset/missing — full zephyrproject west init/update not performed "
            "(multi-GB modules; not installed in this digital pass)"
        )
    if not sdk or not Path(sdk).is_dir():
        blockers.append(
            "ZEPHYR_SDK_INSTALL_DIR unset/missing — full Zephyr SDK ~1.1GB macos-aarch64 "
            "archive download blocked/deferred (policy + disk headroom); freestanding clang "
            "ARM path remains authoritative"
        )

    # Attempt west build only if environment looks complete — never fake a pass.
    west_build_pass = False
    west_build_note = "not_attempted_incomplete_env"
    if west and zephyr_base and sdk and not blockers:
        # Placeholder: a real board app west build would run here.
        west_build_note = "env_present_but_no_app_west_build_invoked"
    else:
        west_build_note = "blocked_incomplete_toolchain"

    tokens = ["RING_PHYSICAL_BOOT_PENDING"]
    if west_build_pass:
        tokens.insert(0, "RING_ZEPHYR_WEST_BUILD_PASS")
    else:
        tokens.insert(0, "RING_ZEPHYR_WEST_BUILD_SOFT_SKIP")

    report = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "west_present": bool(west),
        "west_path": (
            str(west.relative_to(ROOT)) if west and ROOT in west.parents else (str(west) if west else None)
        ),
        "west_version": west_ver,
        "zephyr_base": zephyr_base or None,
        "zephyr_sdk_install_dir": sdk or None,
        "isolated_venv": ".toolchain/west-venv",
        "global_pip_pollution": False,
        "west_build_pass": west_build_pass,
        "west_build_note": west_build_note,
        "blockers": blockers,
        "tokens": tokens,
        "physical_boot_claimed": False,
        "authoritative_build_path": "clang -target armv7em-none-eabi freestanding",
        "full_sdk_size_hint_bytes": 1112069596,
        "disk_policy": "prefer isolated venv; defer multi-GB SDK unless explicitly approved",
    }
    return report


def main() -> int:
    report = probe()
    OUT.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    (OUT / "ZEPHYR_WEST_PROBE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Zephyr / west digital probe",
        "",
        f"Generated: `{report['generated_at_utc']}`",
        "",
        "## Tokens",
        "```text",
        *report["tokens"],
        "```",
        "",
        "## Isolated west",
        f"- west present: `{report['west_present']}`",
        f"- west version: `{report['west_version']}`",
        f"- isolated venv: `{report['isolated_venv']}`",
        f"- global pip pollution: `{report['global_pip_pollution']}`",
        "",
        "## Blockers (exact)",
    ]
    if report["blockers"]:
        for b in report["blockers"]:
            md.append(f"- {b}")
    else:
        md.append("- (none)")
    md += [
        "",
        "## Not claimed",
        "- `RING_ZEPHYR_WEST_BUILD_PASS` (requires successful `west build`)",
        "- Physical flash / boot",
        "",
        "## Authoritative digital path",
        "Freestanding ARM clang + MCUboot DEVELOPMENT pipeline.",
        "",
    ]
    (DOCS / "ZEPHYR_WEST_BLOCKER.md").write_text("\n".join(md), encoding="utf-8")
    (ROOT.parent / "docs" / "ZEPHYR_WEST_BLOCKER.md").write_text("\n".join(md), encoding="utf-8")

    print("ZEPHYR_WEST_PROBE_OK")
    print(" ".join(report["tokens"]))
    for b in report["blockers"]:
        print("BLOCKER:", b)
    # Soft-skip is success for digital closure; hard fail only if we falsely claimed PASS.
    if report["west_build_pass"] is False and "RING_ZEPHYR_WEST_BUILD_PASS" in report["tokens"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
