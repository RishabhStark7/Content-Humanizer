"""Parser for user-provided variant documents in input/ folder."""

from pathlib import Path
from typing import List
from schemas.document import DocumentModel, Section, FAQItem
from schemas.variant import VariantOutput
from src.ingestion.docx_parser import DocxParser
from src.ingestion.md_parser import MarkdownParser


def parse_user_input_variants(input_dir_or_file: Path) -> List[VariantOutput]:
    """Parse user-provided variant documents from input/ folder."""
    variants: List[VariantOutput] = []

    docx_parser = DocxParser()
    md_parser = MarkdownParser()

    if input_dir_or_file.is_dir():
        files = sorted(
            list(input_dir_or_file.glob("*.docx")) +
            list(input_dir_or_file.glob("*.md")) +
            list(input_dir_or_file.glob("*.txt"))
        )
        for idx, f in enumerate(files, 1):
            if f.suffix == ".docx":
                doc = docx_parser.parse(f)
            else:
                doc = md_parser.parse(f)

            variants.append(
                VariantOutput(
                    persona_id=f"input_variant_{idx}",
                    persona_name=f.stem.replace("_", " ").title(),
                    title=doc.title,
                    raw_text=doc.raw_content,
                    sections=doc.sections,
                    faqs=doc.faqs,
                    word_count=doc.total_word_count
                )
            )
    else:
        # Single file - check if it contains multiple "# Variant" headings
        f = input_dir_or_file
        if f.suffix == ".docx":
            doc = docx_parser.parse(f)
        else:
            doc = md_parser.parse(f)

        raw = doc.raw_content
        if "# variant" in raw.lower() or "## variant" in raw.lower():
            # Split single file into multiple variants
            parts = [p.strip() for p in raw.split("# Variant") if p.strip()]
            if len(parts) == 1:
                parts = [p.strip() for p in raw.split("## Variant") if p.strip()]

            for idx, p in enumerate(parts, 1):
                lines = p.splitlines()
                v_name = lines[0].strip(": ").strip() if lines else f"Variant {idx}"
                v_text = "\n".join(lines[1:]).strip() if len(lines) > 1 else p

                # Parse sections inside variant text
                v_doc = parse_markdown_string(v_text, title=f"Variant {idx}: {v_name}")
                variants.append(
                    VariantOutput(
                        persona_id=f"variant_{idx}",
                        persona_name=f"Variant {idx} ({v_name})",
                        title=doc.title,
                        raw_text=v_text,
                        sections=v_doc.sections,
                        faqs=v_doc.faqs,
                        word_count=len(v_text.split())
                    )
                )
        else:
            # Single baseline document
            variants.append(
                VariantOutput(
                    persona_id="input_variant_1",
                    persona_name=f.stem.replace("_", " ").title(),
                    title=doc.title,
                    raw_text=doc.raw_content,
                    sections=doc.sections,
                    faqs=doc.faqs,
                    word_count=doc.total_word_count
                )
            )

    return variants


def parse_markdown_string(text: str, title: str) -> DocumentModel:
    """Helper to convert a markdown string into DocumentModel."""
    sections = []
    current_heading = title
    current_lines = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections.append(Section(heading=current_heading, level=2, content="\n".join(current_lines), word_count=len("\n".join(current_lines).split())))
                current_lines = []
            current_heading = line.replace("## ", "").strip()
        else:
            current_lines.append(line)

    if current_lines:
        sections.append(Section(heading=current_heading, level=2, content="\n".join(current_lines), word_count=len("\n".join(current_lines).split())))

    return DocumentModel(
        title=title,
        metadata={},
        sections=sections,
        faqs=[],
        original_format="md",
        total_word_count=len(text.split()),
        raw_content=text
    )
