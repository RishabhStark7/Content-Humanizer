"""Diversity analysis and filtering report schema."""

from typing import List, Dict, Tuple
from pydantic import BaseModel, Field


class DiversityReport(BaseModel):
    """Report detailing pairwise diversity metrics across variants."""
    total_generated: int = 10
    retained_count: int = 7
    discarded_count: int = 3
    retained_persona_ids: List[str] = Field(default_factory=list)
    discarded_persona_ids: List[str] = Field(default_factory=list)
    similarity_matrix: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    diversity_scores: Dict[str, float] = Field(default_factory=dict)
