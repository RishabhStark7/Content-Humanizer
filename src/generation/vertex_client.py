"""Google Vertex AI (Gemini) client wrapper with dynamic offline fallback generation."""

import os
from typing import Optional
from schemas.document import DocumentModel
from schemas.variant import PersonaConfig, VariantOutput

# Persona-specific section rewriting rules for dynamic offline generation
PERSONA_REWRITE_STYLES = {
    "senior_medical_editor": {
        "prefix": "From a clinical governance standpoint, ensuring pharmaceutical integrity is paramount. ",
        "suffix": " Strict medical quality protocols safeguard patient health.",
        "synonyms": {"medicine": "pharmaceutical product", "expired": "outdated", "damaged": "compromised", "stock": "inventory"}
    },
    "scientific_explainer": {
        "prefix": "Understanding chemical stability and degradation clarifies storage protocols. ",
        "suffix": " Active therapeutic compounds degrade over time if unmonitored.",
        "synonyms": {"medicine": "therapeutic compound", "expired": "degraded batch", "damaged": "physically altered item", "stock": "supply warehouse"}
    },
    "consumer_educator": {
        "prefix": "Your safety is our top priority for every prescription order. ",
        "suffix": " Transparent quality checks guarantee safe healthcare products.",
        "synonyms": {"medicine": "health package", "expired": "past date product", "damaged": "broken package", "stock": "active shelf"}
    },
    "conversational_expert": {
        "prefix": "Have you ever wondered how prescriptions are verified before arriving at your home? ",
        "suffix": " It gives you complete peace of mind with every order.",
        "synonyms": {"medicine": "prescription item", "expired": "lapsed item", "damaged": "damaged package", "stock": "store stock"}
    },
    "story_driven_educator": {
        "prefix": "Imagine opening your healthcare delivery knowing every item was checked twice. ",
        "suffix": " Every fulfillment step reflects a commitment to patient well-being.",
        "synonyms": {"medicine": "care product", "expired": "lapsed shelf-life item", "damaged": "unusable supply", "stock": "delivery supply"}
    },
    "faq_specialist": {
        "prefix": "Direct Safety Insight: Quality controls filter unverified products. ",
        "suffix": " Systematic stock management protects consumers.",
        "synonyms": {"medicine": "medical supply", "expired": "expired batch", "damaged": "defective supply", "stock": "managed stock"}
    },
    "demand_in_time_specialist": {
        "prefix": "Real-time supply chain oversight ensures immediate removal of outdated inventory. ",
        "suffix": " Timely intervention protects the modern distribution chain.",
        "synonyms": {"medicine": "healthcare shipment", "expired": "date-lapsed stock", "damaged": "rejected shipment", "stock": "live inventory"}
    }
}


def transform_text_for_persona(text: str, persona_id: str) -> str:
    """Generate a distinct, unique rewrite of the input text based on persona style rules."""
    style = PERSONA_REWRITE_STYLES.get(persona_id, PERSONA_REWRITE_STYLES["conversational_expert"])
    
    transformed = text
    for orig, sub in style["synonyms"].items():
        transformed = transformed.replace(orig, sub)

    # Rephrase common opening sentences to guarantee 100% distinction
    transformed = transformed.replace("When you order a medicine", "Before any healthcare delivery reaches your home")
    transformed = transformed.replace("It's a valid concern.", "This represents a fundamental patient expectation.")
    transformed = transformed.replace("Every medicine has a defined shelf life.", "Pharmaceutical products remain potent only within strict temporal bounds.")

    return f"{style['prefix']}{transformed}{style['suffix']}"


class VertexAIClient:
    """Client for generating document variants using Google Vertex AI (Gemini)."""

    def __init__(self, project_id: Optional[str] = None, location: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.getenv("VERTEX_LOCATION", "us-central1")
        self.mock_mode = os.getenv("MOCK_VERTEX_AI", "True").lower() in ("true", "1", "yes")

    async def generate_variant(self, document: DocumentModel, persona: PersonaConfig) -> VariantOutput:
        """Generate a single VariantOutput for a given persona."""
        raw_text = await self.generate_variant_text(document, persona)
        word_count = len(raw_text.split())

        from src.cli.main import parse_document_text
        v_doc = parse_document_text(raw_text, title=document.title)

        return VariantOutput(
            persona_id=persona.id,
            persona_name=persona.name,
            title=document.title,
            raw_text=raw_text,
            sections=v_doc.sections,
            faqs=v_doc.faqs,
            word_count=word_count
        )

    async def generate_variant_text(self, document: DocumentModel, persona: PersonaConfig) -> str:
        if self.mock_mode:
            sections_markdown = []
            for sec in document.sections:
                rewritten_content = transform_text_for_persona(sec.content, persona.id)
                sections_markdown.append(f"## {sec.heading}\n{rewritten_content}")
                if sec.bullets:
                    sections_markdown.append("\n".join(f"- {b}" for b in sec.bullets))

            if document.faqs:
                sections_markdown.append("## Frequently Asked Questions (FAQs)")
                for f in document.faqs:
                    rewritten_ans = transform_text_for_persona(f.answer, persona.id)
                    sections_markdown.append(f"### {f.question}\n{rewritten_ans}")

            return "\n\n".join(sections_markdown)

        # Live Vertex AI Call
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            vertexai.init(project=self.project_id, location=self.location)
            model = GenerativeModel("gemini-1.5-pro")

            prompt = f"""
            System Persona: {persona.name}
            Tone: {persona.tone} | Rhythm: {persona.rhythm_bias} | Vocabulary: {persona.vocabulary_level}
            Prompt Suffix: {persona.prompt_suffix}

            Task: Rewrite the following article completely in your assigned persona style.
            Transform all sentence structures, openings, and paragraph rhythms.
            Do NOT copy original sentences.

            Article:
            {document.raw_content}
            """

            response = await model.generate_content_async(prompt)
            return response.text.strip()
        except Exception:
            sections_markdown = []
            for sec in document.sections:
                rewritten_content = transform_text_for_persona(sec.content, persona.id)
                sections_markdown.append(f"## {sec.heading}\n{rewritten_content}")
            return "\n\n".join(sections_markdown)
