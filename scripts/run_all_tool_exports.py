#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from edge_io_node.tool_adapters import oran_kpi_export, aerial_kpi_export, measurement_validation
oran_kpi_export.export()
aerial_kpi_export.export()
measurement_validation.report()
