"""Validate Edge measurement batches against canonical schemas."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from .schema_loader import resolve_schema_dir


def _load_fieldkit_validator(schema_dir: Path):
    candidate = schema_dir.parent / "scripts" / "validate_contract.py"
    if not candidate.is_file():
        raise FileNotFoundError(f"Missing field-kit validator at {candidate}")
    spec = importlib.util.spec_from_file_location("gate2_validate_contract", candidate)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load validator from {candidate}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def validate_batch(
    document: dict[str, Any] | Path,
    schema_dir: str | Path | None = None,
) -> dict[str, Any]:
    path_or_doc = document
    schema_path = resolve_schema_dir(schema_dir)
    mod = _load_fieldkit_validator(schema_path)
    if isinstance(path_or_doc, Path):
        doc = json.loads(path_or_doc.read_text(encoding="utf-8"))
    else:
        doc = path_or_doc
    return mod.validate_document(
        doc,
        schema_path,
        expected_schema_name="gunnchos.edge_measurement_batch",
        enforce_privacy=True,
    )
