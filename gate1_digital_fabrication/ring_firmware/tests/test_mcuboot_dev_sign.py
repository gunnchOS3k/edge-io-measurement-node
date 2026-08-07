from pathlib import Path
import json, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]

def test_mcuboot_sign_and_tamper(tmp_path=None):
    subprocess.check_call(["make", "mcuboot-sign"], cwd=ROOT)
    report = json.loads((ROOT / "build/out/mcuboot/mcuboot_dev_sign_report.json").read_text())
    assert report["verify_signed_ok"] is True
    assert report["verify_tampered_ok"] is False
    assert report["physical_boot_claim"] is False
    assert "RING_MCU_TARGET_FIRMWARE_BUILD_PASS" in report["status_tokens"]
