.PHONY: test demo demo-research benchmark-toy map

test:
	pytest -q

demo:
	PYTHONPATH=src python3 -m edge_io_node.demo --toy
