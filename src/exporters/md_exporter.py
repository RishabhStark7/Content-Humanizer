"""Exporter for Markdown (.md) format with YAML frontmatter."""

from pathlib import Path
from typing import Union
from schemas.document import DocumentModel
from schemas.validation import ValidationReport


def export_to_markdown(
    document: DocumentModel,
    output_path: Union[str, Path],
    validation_report: ValidationReport = None
) -> Path:
    """Export DocumentModel to clean Markdown file.

    Args:
        document: Synthesized DocumentModel.
        output_path: Target output path.
        validation_report: Optional ValidationReport.

    Returns:
        Saved file Path.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    lines = ["---", f"title: \"{document.title}\"", f"word_count: {document.total_word_count}"]
    if validation_report:
        lines.append(f"validation_passed: {validation_report.passed}")
        lines.append(f"readability_grade: {validation_report.metrics.get('flesch_kincaid_grade', 8.0)}")
    lines.append("---\n")

    lines.append(f"# {document.title}\n")

    for sec in document.sections:
        if sec.level == 1 and sec.heading.strip().lower() == document.title.strip().lower():
            continue
        hashes = "#" * max(1, min(6, sec.level))
        lines.append(f"{hashes} {sec.heading}\n")
        lines.append(f"{sec.content}\n")
        if sec.bullets:
            for b in sec.bullets:
                lines.append(f"- {b}")
            lines.append("")

    if document.faqs:
        lines.append("## Frequently Asked Questions (FAQs)\n")
        for f in document.faqs:
            lines.append(f"### {f.question}\n")
            lines.append(f"{f.answer}\n")

    content = "\n".join(lines)
    out_file.write_text(content, encoding="utf-8")
    return out_file
