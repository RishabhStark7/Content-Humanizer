"""Prompt builder combining constitution, input context, and persona instructions."""

from pathlib import Path
from schemas.document import DocumentModel
from schemas.variant import PersonaConfig


def build_persona_prompt(document: DocumentModel, persona: PersonaConfig) -> str:
    """Construct full prompt for generating a persona variant.

    Args:
        document: Baseline DocumentModel.
        persona: PersonaConfig definition.

    Returns:
        Formatted prompt string.
    """
    constitution_path = Path("prompts/constitution.txt")
    constitution = constitution_path.read_text(encoding="utf-8") if constitution_path.exists() else "EDITORIAL CONSTITUTION: Maintain high factual accuracy and clear rhythm."

    sections_text = "\n\n".join([
        f"## {s.heading}\n{s.content}\n" + ("\n".join(f"- {b}" for b in s.bullets) if s.bullets else "")
        for s in document.sections
    ])

    faqs_text = "\n\n".join([
        f"Q: {f.question}\nA: {f.answer}"
        for f in document.faqs
    ])

    prompt = f"""{constitution}

PERSONA INSTRUCTIONS:
Persona Name: {persona.name}
Tone: {persona.tone}
Rhythm Bias: {persona.rhythm_bias}
Vocabulary Level: {persona.vocabulary_level}
Transition Style: {persona.transition_style}
Specific Instruction: {persona.prompt_suffix}

ARTICLE TITLE: {document.title}

TARGET CONTENT & SECTIONS:
{sections_text}

MANDATORY FREQUENTLY ASKED QUESTIONS (Minimum 7 FAQs, 3-4 lines per answer):
{faqs_text}

REWRITE TASK:
Rewrite the article completely following your designated persona while strictly preserving all facts, heading structures, bullet lists, and FAQs.
Format your output in clean Markdown starting with '# {document.title}'.
"""
    return prompt
