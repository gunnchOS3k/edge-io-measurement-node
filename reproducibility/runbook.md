# Runbook

```bash
pip install -r requirements.txt
pytest -q
PYTHONPATH=src python3 -m edge_io_node.demo --toy
```

Expected: exit 0, artifact under results/ or docs/generated/.
