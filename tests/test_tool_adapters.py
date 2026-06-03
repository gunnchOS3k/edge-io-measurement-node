import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from edge_io_node.tool_adapters.oran_kpi_export import export
def test_oran(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert export("gaza").exists()
