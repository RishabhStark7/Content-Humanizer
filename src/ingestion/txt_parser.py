"""Plain text document parser."""

from pathlib import Path
from typing import Union
from .base import BaseParser
from schemas.document import DocumentModel, Section, FAQItem


class TextParser(BaseParser):
    """Parser for Plain Text (.txt) documents."""

    def parse(self, file_path_or_content: Union[str, Path]) -> DocumentModel:
        if isinstance(file_path_or_content, Path) or (isinstance(file_path_or_content, str) and Path(file_path_or_content).exists()):
            path = Path(file_path_or_content)
            raw_text = path.read_text(encoding="utf-8")
            default_title = path.stem.replace("_", " ").replace("-", " ").title()
        else:
            raw_text = str(file_path_or_content)
            default_title = "Untitled Text Article"

        lines = raw_text.splitlines()
        sections = []
        faqs = []
        current_heading = default_title
        current_level = 1
        current_paras = []
        current_bullets = []

        title = default_title
        first_line = True

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if first_line:
                title = stripped
                current_heading = stripped
                first_line = False
                continue

            # Heuristics for heading in plain text: short line, upper case or ending without period
            if len(stripped) < 60 and (stripped.isupper() or not stripped.endswith(".")):
                if current_paras or current_bullets:
                    sections.append(
                        Section(
                            heading=current_heading,
                            level=current_level,
                            content="\n\n".join(current_paras),
                            bullets=current_bullets,
                            word_count=sum(len(p.split()) for p in current_paras)
                        )
                    )
                    current_paras = []
                    current_bullets = []
                current_heading = stripped
                current_level = 2
            elif stripped.startswith("- ") or stripped.startswith("* "):
                current_bullets.append(stripped.lstrip("-* ").strip())
            else:
                current_paras.append(stripped)

        if current_paras or current_bullets:
            sections.append(
                Section(
                    heading=current_heading,
                    level=current_level,
                    content="\n\n".join(current_paras),
                    bullets=current_bullets,
                    word_count=sum(len(p.split()) for p in current_paras)
                )
            )

        total_words = len(raw_text.split())

        return DocumentModel(
            title=title,
            sections=sections,
            faqs=faqs,
            original_format="text",
            total_word_count=total_words,
            raw_content=raw_text
        )
