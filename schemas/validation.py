"""Validation report schema for editorial guardrails."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class GuardrailCheckResult(BaseModel):
    """Result of an individual guardrail check."""
    name: str
    passed: bool
    score: float = 1.0
    details: str = ""


class ValidationReport(BaseModel):
    """Consolidated validation report for an output article."""
    passed: bool = True
    word_count_check: GuardrailCheckResult
    readability_check: GuardrailCheckResult
    faq_check: GuardrailCheckResult
    heading_hierarchy_check: GuardrailCheckResult
    seo_check: GuardrailCheckResult
    geo_aeo_check: GuardrailCheckResult
    cliche_check: GuardrailCheckResult
    metrics: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
