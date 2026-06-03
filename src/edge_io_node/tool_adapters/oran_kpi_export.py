import yaml
from pathlib import Path
def export(site_id: str = "gary") -> Path:
    out = Path("results/tool_exports/edge_io_oran_kpis.yaml")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.dump({"site_id": site_id, "kpis": ["latency_ms", "jitter_ms", "packet_loss_pct"], "evidence_status": "stub"}), encoding="utf-8")
    return out
