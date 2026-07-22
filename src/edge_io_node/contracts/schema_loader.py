"""Resolve Gate 2 schema directory."""
from __future__ import annotations

import os
from pathlib import Path


def resolve_schema_dir(schema_dir: str | Path | None = None) -> Path:
    if schema_dir is not None:
        return Path(schema_dir).expanduser().resolve()
    env = os.environ.get("GATE2_CONTRACTS_DIR")
    if env:
        return Path(env).expanduser().resolve()
    # Preferred sibling field-kit path
    sibling = (
        Path(__file__).resolve().parents[4]
        / "gunnchos-7gc-ai-ran-field-kit"
        / "contracts"
    )
    if sibling.is_dir():
        return sibling
    raise FileNotFoundError(
        "Schema directory not found. Pass --schema-dir or set GATE2_CONTRACTS_DIR"
    )
