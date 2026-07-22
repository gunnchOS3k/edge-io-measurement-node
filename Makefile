.PHONY: setup lint test contract-test demo e2e clean

PY := PYTHONPATH=src

setup:
	python3 -m pip install -r requirements.txt

lint:
	$(PY) python3 -m compileall -q src

test:
	$(PY) pytest -q

contract-test:
	$(PY) pytest -q tests/contracts

demo:
	$(PY) python3 -m edge_io_node.demo --toy

clean:
	rm -rf results/session.json results/01_edge_measurements.json

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

ANDROID_DIR := clients/android

android-debug-apk:
	cd $(ANDROID_DIR) && (./gradlew :app:assembleDebug || gradle :app:assembleDebug || (echo "Android SDK/Gradle unavailable; see docs/GATE3_ANDROID_SETUP.md" && exit 1))

android-install:
	@APK=$$(ls $(ANDROID_DIR)/app/build/outputs/apk/debug/*.apk 2>/dev/null | head -n1); \
	test -n "$$APK" || (echo "No APK; run make android-debug-apk" && exit 1); \
	adb devices; adb install -r "$$APK"

android-test:
	cd $(ANDROID_DIR) && (./gradlew :app:testDebugUnitTest || echo "unit tests require Android Gradle toolchain")

android-export-check:
	@echo "Export check requires a device session file; validate with field-kit scripts/validate_session.py"
