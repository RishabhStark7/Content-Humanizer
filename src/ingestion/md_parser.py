"""Markdown document parser."""

import re
from pathlib import Path
from typing import Union
from .base import BaseParser
from schemas.document import DocumentModel, Section, FAQItem


class MarkdownParser(BaseParser):
    """Parser for Markdown (.md, .markdown) documents."""

    def parse(self, file_path_or_content: Union[str, Path]) -> DocumentModel:
        if isinstance(file_path_or_content, Path) or (isinstance(file_path_or_content, str) and Path(file_path_or_content).exists()):
            path = Path(file_path_or_content)
            raw_text = path.read_text(encoding="utf-8")
            default_title = path.stem.replace("_", " ").replace("-", " ").title()
        else:
            raw_text = str(file_path_or_content)
            default_title = "Untitled Markdown Article"

        title = default_title
        lines = raw_text.splitlines()
        sections = []
        faqs = []
        current_heading = "Introduction"
        current_level = 2
        current_paras = []
        current_bullets = []

        in_faq_section = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Heading matching
            if stripped.startswith("#"):
                match = re.match(r"^(#+)\s+(.*)$", stripped)
                if match:
                    hashes, heading_text = match.groups()
                    level = len(hashes)

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

                    if level == 1:
                        title = heading_text
                        current_heading = heading_text
                        current_level = 1
                    else:
                        current_heading = heading_text
                        current_level = level

                    in_faq_section = "faq" in heading_text.lower() or "frequently asked" in heading_text.lower()
                    continue

            # Bullet items
            if stripped.startswith("- ") or stripped.startswith("* ") or re.match(r"^\d+\.\s+", stripped):
                bullet_text = re.sub(r"^([-*]|\d+\.)\s+", "", stripped)
                current_bullets.append(bullet_text)
                continue

            # FAQ matching format "Q: Question" / "A: Answer"
            if in_faq_section and ("?" in stripped or stripped.lower().startswith("q:")):
                # If paragraph has Q/A pattern
                current_paras.append(stripped)
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

        # Extract FAQs from sections if in FAQ section
        faq_sections = [s for s in sections if "faq" in s.heading.lower()]
        for s in faq_sections:
            lines_in_sec = s.content.split("\n\n")
            q_tmp = None
            a_lines = []
            for l in lines_in_sec:
                if l.startswith("Q:") or l.endswith("?"):
                    if q_tmp and a_lines:
                        ans = "\n".join(a_lines)
                        faqs.append(FAQItem(question=q_tmp, answer=ans, line_count=len(a_lines), word_count=len(ans.split())))
                        a_lines = []
                    q_tmp = l.replace("Q:", "").strip()
                elif q_tmp:
                    a_lines.append(l)
            if q_tmp and a_lines:
                ans = "\n".join(a_lines)
                faqs.append(FAQItem(question=q_tmp, answer=ans, line_count=len(a_lines), word_count=len(ans.split())))

        total_words = len(raw_text.split())

        return DocumentModel(
            title=title,
            sections=sections,
            faqs=faqs,
            original_format="markdown",
            total_word_count=total_words,
            raw_content=raw_text
        )
