"""HTML document parser using BeautifulSoup."""

from pathlib import Path
from typing import Union
from bs4 import BeautifulSoup
from .base import BaseParser
from schemas.document import DocumentModel, Section, FAQItem


class HtmlParser(BaseParser):
    """Parser for HTML (.html, .htm) documents."""

    def parse(self, file_path_or_content: Union[str, Path]) -> DocumentModel:
        if isinstance(file_path_or_content, Path) or (isinstance(file_path_or_content, str) and Path(file_path_or_content).exists()):
            path = Path(file_path_or_content)
            raw_html = path.read_text(encoding="utf-8")
            default_title = path.stem.replace("_", " ").replace("-", " ").title()
        else:
            raw_html = str(file_path_or_content)
            default_title = "Untitled HTML Article"

        soup = BeautifulSoup(raw_html, "html.parser")
        h1_tag = soup.find("h1")
        title = h1_tag.get_text().strip() if h1_tag else default_title

        sections = []
        faqs = []
        current_heading = "Introduction"
        current_level = 2
        current_paras = []
        current_bullets = []

        body = soup.find("body") or soup

        for elem in body.find_all(["h1", "h2", "h3", "h4", "p", "ul", "ol"]):
            tag_name = elem.name.lower()
            text = elem.get_text().strip()
            if not text:
                continue

            if tag_name in ["h1", "h2", "h3", "h4"]:
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

                level = int(tag_name[1])
                current_heading = text
                current_level = level
            elif tag_name in ["ul", "ol"]:
                for li in elem.find_all("li"):
                    current_bullets.append(li.get_text().strip())
            elif tag_name == "p":
                current_paras.append(text)

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

        raw_text = soup.get_text(separator="\n\n")
        total_words = len(raw_text.split())

        return DocumentModel(
            title=title,
            sections=sections,
            faqs=faqs,
            original_format="html",
            total_word_count=total_words,
            raw_content=raw_text
        )
