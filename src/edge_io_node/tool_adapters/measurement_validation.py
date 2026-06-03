from pathlib import Path
def report() -> Path:
    out = Path("results/tool_exports/measurement_validation_report.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("# Measurement validation\n\nSmoke schema alignment only.\n", encoding="utf-8")
    return out
