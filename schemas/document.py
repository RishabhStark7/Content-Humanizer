"""Document parsing and structured section representation."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FAQItem(BaseModel):
    """Structured FAQ question and multi-line answer."""
    question: str
    answer: str
    line_count: int = 1
    word_count: int = 0


class Section(BaseModel):
    """Structured article section containing heading and body content."""
    heading: str
    level: int = 2  # 1 for H1, 2 for H2, 3 for H3, etc.
    content: str
    bullets: List[str] = Field(default_factory=list)
    tables: List[List[List[str]]] = Field(default_factory=list)
    word_count: int = 0


class DocumentModel(BaseModel):
    """Representation of an ingested document."""
    title: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sections: List[Section] = Field(default_factory=list)
    faqs: List[FAQItem] = Field(default_factory=list)
    original_format: str = "markdown"  # docx, markdown, html, text
    total_word_count: int = 0
    raw_content: str = ""
