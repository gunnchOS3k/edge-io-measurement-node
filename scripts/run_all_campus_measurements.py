#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from edge_io_node.campus_reports import run_all_campus
run_all_campus("local-safe")
