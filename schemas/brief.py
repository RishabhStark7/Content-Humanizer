"""Content brief schema for Mode B workflow."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ContentBriefModel(BaseModel):
    """Input specification for generating new content from scratch."""
    topic: str
    objective: str
    target_audience: str
    tone: str = "Knowledgeable, professional, accessible"
    target_word_count: int = 1500
    keywords: List[str] = Field(default_factory=list)
    geo_aeo_entities: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    brand_guidelines: Optional[str] = None
