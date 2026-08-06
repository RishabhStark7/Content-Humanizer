"""Variant generator orchestrating parallel multi-persona generation."""

import asyncio
from pathlib import Path
from typing import List
import yaml
from schemas.document import DocumentModel
from schemas.variant import PersonaConfig, VariantOutput
from .vertex_client import VertexAIClient


def load_all_personas() -> List[PersonaConfig]:
    """Load all 10 persona YAML files from personas/ directory.

    Returns:
        List of 10 PersonaConfig objects.
    """
    persona_dir = Path("personas")
    personas = []
    if persona_dir.exists():
        for p_path in persona_dir.glob("*.yaml"):
            with open(p_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                personas.append(PersonaConfig(**data))

    if not personas:
        # Fallback inline personas if directory missing
        personas = [
            PersonaConfig(id="senior_medical_editor", name="Senior Medical Editor", tone="Formal yet conversational, clinical", rhythm_bias="Measured", vocabulary_level="Clinical", transition_style="Logical", prompt_suffix="Senior medical view."),
            PersonaConfig(id="scientific_explainer", name="Scientific Explainer", tone="Formal yet conversational, analytical", rhythm_bias="Explanatory", vocabulary_level="Scientific", transition_style="Cause and effect", prompt_suffix="Scientific view."),
            PersonaConfig(id="technical_writer", name="Technical Writer", tone="Formal yet conversational, structured", rhythm_bias="Concise", vocabulary_level="Direct", transition_style="Sequential", prompt_suffix="Technical view."),
            PersonaConfig(id="consumer_educator", name="Consumer Educator", tone="Formal yet conversational, warm", rhythm_bias="Practical", vocabulary_level="Everyday", transition_style="Practical", prompt_suffix="Consumer view."),
            PersonaConfig(id="conversational_expert", name="Conversational Expert", tone="Formal yet conversational, engaging", rhythm_bias="Dynamic", vocabulary_level="Conversational", transition_style="Smooth", prompt_suffix="Conversational view."),
            PersonaConfig(id="story_driven_educator", name="Story-Driven Educator", tone="Formal yet conversational, narrative", rhythm_bias="Varied", vocabulary_level="Descriptive", transition_style="Temporal", prompt_suffix="Story view."),
            PersonaConfig(id="magazine_writer", name="Magazine Writer", tone="Formal yet conversational, polished", rhythm_bias="Sophisticated", vocabulary_level="Elegant", transition_style="Editorial", prompt_suffix="Magazine view."),
            PersonaConfig(id="faq_specialist", name="FAQ Specialist", tone="Formal yet conversational, direct", rhythm_bias="Answer-first", vocabulary_level="Clear", transition_style="Direct Q&A", prompt_suffix="FAQ view."),
            PersonaConfig(id="evidence_first_writer", name="Evidence-First Writer", tone="Formal yet conversational, empirical", rhythm_bias="Data-backed", vocabulary_level="Analytical", transition_style="Evidence-linking", prompt_suffix="Evidence view."),
            PersonaConfig(id="demand_in_time_specialist", name="Time & Demand Specialist", tone="Formal yet conversational, adaptive", rhythm_bias="Adaptive", vocabulary_level="Contemporary", transition_style="Demand-aligned", prompt_suffix="Time and demand view."),
        ]
    return personas


async def generate_10_variants(document: DocumentModel, client: VertexAIClient = None) -> List[VariantOutput]:
    """Generate 10 distinct editorial variants concurrently using Vertex AI.

    Args:
        document: Ingested baseline DocumentModel.
        client: Optional pre-configured VertexAIClient.

    Returns:
        List of 10 VariantOutput instances.
    """
    client = client or VertexAIClient()
    personas = load_all_personas()

    tasks = [client.generate_variant(document, persona) for persona in personas]
    variants = await asyncio.gather(*tasks)
    return list(variants)
