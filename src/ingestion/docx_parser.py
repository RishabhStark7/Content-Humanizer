"""Docx parser using python-docx."""

from pathlib import Path
from typing import Union
import docx
from .base import BaseParser
from schemas.document import DocumentModel, Section, FAQItem


class DocxParser(BaseParser):
    """Parser for Microsoft Word (.docx) documents."""

    def parse(self, file_path_or_content: Union[str, Path]) -> DocumentModel:
        doc_path = Path(file_path_or_content)
        if not doc_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {doc_path}")

        doc = docx.Document(str(doc_path))
        title = doc_path.stem.replace("_", " ").replace("-", " ").title()
        sections = []
        faqs = []
        current_heading = "Introduction"
        current_level = 2
        current_paras = []
        current_bullets = []
        raw_text_parts = []

        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue

            raw_text_parts.append(text)
            style_name = p.style.name.lower() if p.style else ""

            if style_name.startswith("heading 1") or style_name.startswith("title"):
                title = text
            elif style_name.startswith("heading") or text.startswith("#"):
                if current_paras or current_bullets:
                    sections.append(
                        Section(
                            heading=current_heading,
                            level=current_level,
                            content="\n\n".join(current_paras),
                            bullets=current_bullets,
                            word_count=sum(len(c.split()) for c in current_paras)
                        )
                    )
                    current_paras = []
                    current_bullets = []

                if style_name.startswith("heading 2"):
                    current_level = 2
                elif style_name.startswith("heading 3"):
                    current_level = 3
                else:
                    current_level = 2
                current_heading = text.lstrip("#").strip()
            elif style_name.startswith("list") or p.text.startswith("•") or p.text.startswith("-"):
                current_bullets.append(text.lstrip("•- ").strip())
            else:
                if text.startswith("Q:") or "faq" in current_heading.lower():
                    if "?" in text and ":" in text:
                        q_part, a_part = text.split(":", 1)
                        faqs.append(
                            FAQItem(
                                question=q_part.strip(),
                                answer=a_part.strip(),
                                line_count=len(a_part.splitlines()),
                                word_count=len(a_part.split())
                            )
                        )
                    else:
                        current_paras.append(text)
                else:
                    current_paras.append(text)

        if current_paras or current_bullets:
            sections.append(
                Section(
                    heading=current_heading,
                    level=current_level,
                    content="\n\n".join(current_paras),
                    bullets=current_bullets,
                    word_count=sum(len(c.split()) for c in current_paras)
                )
            )

        raw_full = "\n\n".join(raw_text_parts)
        total_words = len(raw_full.split())

        return DocumentModel(
            title=title,
            sections=sections,
            faqs=faqs,
            original_format="docx",
            total_word_count=total_words,
            raw_content=raw_full
        )
