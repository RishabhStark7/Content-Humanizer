"""Exporter for styled semantic HTML (.html) format."""

from pathlib import Path
from typing import Union
from schemas.document import DocumentModel
from schemas.validation import ValidationReport


def export_to_html(
    document: DocumentModel,
    output_path: Union[str, Path],
    validation_report: ValidationReport = None
) -> Path:
    """Export DocumentModel to semantic styled HTML5 file.

    Args:
        document: Synthesized DocumentModel.
        output_path: Target path.
        validation_report: Optional ValidationReport.

    Returns:
        Saved file Path.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    html_parts = [
        "<!DOCTYPE html>",
        "<html lang=\"en\">",
        "<head>",
        "  <meta charset=\"UTF-8\">",
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
        f"  <title>{document.title}</title>",
        "  <style>",
        "    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #2d3748; background: #f7fafc; }",
        "    h1 { color: #1a202c; font-size: 2.2rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }",
        "    h2 { color: #2b6cb0; font-size: 1.6rem; margin-top: 30px; }",
        "    h3 { color: #2c5282; font-size: 1.2rem; }",
        "    p { margin-bottom: 1.2rem; }",
        "    ul { background: #edf2f7; padding: 15px 30px; border-radius: 6px; }",
        "    .faq-item { background: #fff; border-left: 4px solid #3182ce; padding: 15px 20px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }",
        "  </style>",
        "</head>",
        "<body>",
        f"  <h1>{document.title}</h1>",
    ]

    for sec in document.sections:
        tag = f"h{max(1, min(6, sec.level))}"
        html_parts.append(f"  <{tag}>{sec.heading}</{tag}>")
        for para in sec.content.split("\n\n"):
            if para.strip():
                html_parts.append(f"  <p>{para.strip()}</p>")

        if sec.bullets:
            html_parts.append("  <ul>")
            for b in sec.bullets:
                html_parts.append(f"    <li>{b}</li>")
            html_parts.append("  </ul>")

    if document.faqs:
        html_parts.append("  <h2>Frequently Asked Questions (FAQs)</h2>")
        for f in document.faqs:
            html_parts.append("  <div class=\"faq-item\">")
            html_parts.append(f"    <h3>{f.question}</h3>")
            html_parts.append(f"    <p>{f.answer}</p>")
            html_parts.append("  </div>")

    html_parts.extend(["</body>", "</html>"])

    out_file.write_text("\n".join(html_parts), encoding="utf-8")
    return out_file
