"""Export Edge-IO batches into the canonical Gate 2 measurement document."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from edge_io_node.contracts.validate import validate_batch


def export_batch_to_7gc(
    input_path: Path,
    output_path: Path,
    schema_dir: str | Path | None = None,
) -> Path:
    """Validate and copy a measurement batch for 7GC ingestion.

    No manual field rewriting is performed. The document must already be
    schema-valid and privacy-safe.
    """
    document: dict[str, Any] = json.loads(input_path.read_text(encoding="utf-8"))
    validate_batch(document, schema_dir=schema_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Preserve bytes exactly after validation by rewriting canonical JSON
    output_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    validate_batch(output_path, schema_dir=schema_dir)
    return output_path


def copy_validated(
    input_path: Path,
    output_path: Path,
    schema_dir: str | Path | None = None,
) -> Path:
    validate_batch(input_path, schema_dir=schema_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(input_path, output_path)
    return output_path
