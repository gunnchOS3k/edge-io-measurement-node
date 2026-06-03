.PHONY: test demo e2e

PY := PYTHONPATH=src

test:
	$(PY) pytest -q

demo:
	$(PY) python3 -m edge_io_node.demo --toy

e2e:
	@mkdir -p results/e2e results/campus_measurements
	$(PY) pytest -q 2>&1 | tee results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m edge_io_node.cli run-all-campus --mode local-safe >> results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m edge_io_node.demo --toy >> results/e2e/e2e_terminal_output.txt
	python3 scripts/run_all_tool_exports.py 2>> results/e2e/e2e_terminal_output.txt || true
	$(MAKE) e2e-tooling 2>> results/e2e/e2e_terminal_output.txt || true
	python3 scripts/e2e_check_required_artifacts.py


# Smoke test only — not evidence of readiness
smoke: e2e


e2e-tooling:
	@mkdir -p results/tool_exports
	python3 scripts/run_all_tool_exports.py 2>/dev/null || python3 scripts/check_optional_backends.py || true

e2e-sionna e2e-deepmimo e2e-aerial e2e-oran:
	@echo "Optional target $@ — requires external install; not run in default CI"
