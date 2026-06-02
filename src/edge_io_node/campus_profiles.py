"""Campus measurement profiles."""
from pathlib import Path
import yaml

DIR = Path(__file__).resolve().parents[2] / "configs" / "campus_measurement_profiles"


def list_campus_profiles() -> list[str]:
    return sorted(p.stem for p in DIR.glob("*.yaml"))


def load_campus_profile(site_id: str) -> dict:
    path = DIR / f"{site_id}.yaml"
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data.get("site_id") != site_id:
        raise ValueError("site_id mismatch")
    return data
