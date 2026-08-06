"""Router for auto-selecting appropriate document parser."""

from pathlib import Path
from typing import Union
from schemas.document import DocumentModel
from .docx_parser import DocxParser
from .md_parser import MarkdownParser
from .html_parser import HtmlParser
from .txt_parser import TextParser


def parse_document(file_path_or_content: Union[str, Path]) -> DocumentModel:
    """Parse file or raw content using appropriate parser based on file extension or structure.

    Args:
        file_path_or_content: File path or raw text string.

    Returns:
        DocumentModel instance.
    """
    if isinstance(file_path_or_content, Path) or (isinstance(file_path_or_content, str) and Path(file_path_or_content).exists()):
        path = Path(file_path_or_content)
        ext = path.suffix.lower()

        if ext == ".docx":
            return DocxParser().parse(path)
        elif ext in [".md", ".markdown"]:
            return MarkdownParser().parse(path)
        elif ext in [".html", ".htm"]:
            return HtmlParser().parse(path)
        else:
            return TextParser().parse(path)

    # String content fallback
    content = str(file_path_or_content)
    if "<html" in content.lower() or "<body" in content.lower():
        return HtmlParser().parse(content)
    elif "# " in content or "## " in content:
        return MarkdownParser().parse(content)
    else:
        return TextParser().parse(content)
