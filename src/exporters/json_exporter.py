"""Exporter for structured JSON format."""

import json
from pathlib import Path
from typing import Union
from schemas.document import DocumentModel
from schemas.validation import ValidationReport


def export_to_json(
    document: DocumentModel,
    output_path: Union[str, Path],
    validation_report: ValidationReport = None
) -> Path:
    """Export DocumentModel and metadata to structured JSON file.

    Args:
        document: Synthesized DocumentModel.
        output_path: Target JSON output path.
        validation_report: Optional ValidationReport.

    Returns:
        Saved file Path.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    data = document.model_dump()
    if validation_report:
        data["validation_report"] = validation_report.model_dump()

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return out_file
