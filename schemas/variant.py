"""Persona definition and generated variant schema."""

from typing import List
from pydantic import BaseModel, Field
from .document import Section, FAQItem


class PersonaConfig(BaseModel):
    """Editorial persona configuration."""
    id: str
    name: str
    tone: str
    rhythm_bias: str
    vocabulary_level: str
    transition_style: str
    prompt_suffix: str


class VariantOutput(BaseModel):
    """Generated article variant produced by one editorial persona."""
    persona_id: str
    persona_name: str
    title: str
    sections: List[Section] = Field(default_factory=list)
    faqs: List[FAQItem] = Field(default_factory=list)
    raw_text: str = ""
    word_count: int = 0
