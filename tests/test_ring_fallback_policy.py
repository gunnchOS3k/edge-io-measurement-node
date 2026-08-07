from pathlib import Path
try:
    import yaml
except ImportError:
    yaml = None
p = Path(__file__).resolve().parents[1] / "firmware/ring_calibration/fallback_policy.yaml"
data = yaml.safe_load(p.read_text(encoding="utf-8"))
assert "host_controls" in data["modes"]
assert data["physical_status"] == "PHYSICAL_PENDING"
