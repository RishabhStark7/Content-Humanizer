"""Exporter for Microsoft Word (.docx) format."""

from pathlib import Path
from typing import Union
import docx
from schemas.document import DocumentModel
from schemas.validation import ValidationReport


def export_to_docx(
    document: DocumentModel,
    output_path: Union[str, Path],
    validation_report: ValidationReport = None
) -> Path:
    """Export DocumentModel to styled DOCX document.

    Args:
        document: Synthesized DocumentModel.
        output_path: Target path for .docx output file.
        validation_report: Optional ValidationReport to embed as metadata.

    Returns:
        Path object of saved file.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    doc = docx.Document()
    doc.add_heading(document.title, level=0)

    for sec in document.sections:
        doc.add_heading(sec.heading, level=sec.level)
        for para in sec.content.split("\n\n"):
            if para.strip():
                doc.add_paragraph(para.strip())

        for b in sec.bullets:
            doc.add_paragraph(b, style="List Bullet")

    if document.faqs:
        doc.add_heading("Frequently Asked Questions (FAQs)", level=2)
        for faq in document.faqs:
            doc.add_heading(faq.question, level=3)
            doc.add_paragraph(faq.answer)

    doc.save(str(out_file))
    return out_file
