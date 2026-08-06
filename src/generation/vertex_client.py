"""Vertex AI API client wrapper with async support and offline mock fallback."""

import os
import asyncio
from typing import Optional
from schemas.variant import PersonaConfig, VariantOutput
from schemas.document import DocumentModel, Section, FAQItem
from .prompt_builder import build_persona_prompt


class VertexAIClient:
    """Client for generating content via Google Vertex AI (Gemini) with mock fallback."""

    def __init__(
        self,
        project: Optional[str] = None,
        location: str = "us-central1",
        model_name: str = "gemini-2.5-flash",
        mock_mode: bool = True
    ):
        self.project = project or os.getenv("GOOGLE_CLOUD_PROJECT", "mock-project")
        self.location = location or os.getenv("VERTEX_LOCATION", "us-central1")
        self.model_name = model_name
        self.mock_mode = mock_mode or os.getenv("MOCK_VERTEX_AI", "True").lower() in ["true", "1", "yes"]

    async def generate_variant(self, document: DocumentModel, persona: PersonaConfig) -> VariantOutput:
        """Generate an article variant using a specific persona.

        Args:
            document: Input baseline DocumentModel.
            persona: Targeted PersonaConfig.

        Returns:
            VariantOutput containing persona-styled article content.
        """
        prompt = build_persona_prompt(document, persona)

        if self.mock_mode:
            return self._generate_mock_variant(document, persona)

        try:
            # Import vertexai / google.genai dynamically
            import vertexai
            from vertexai.generative_models import GenerativeModel

            vertexai.init(project=self.project, location=self.location)
            model = GenerativeModel(self.model_name)
            response = await asyncio.to_thread(model.generate_content, prompt)
            raw_text = response.text
            return self._parse_generated_text(raw_text, persona, document)
        except Exception as e:
            # Fallback to mock on connection/credential error
            return self._generate_mock_variant(document, persona, error_msg=str(e))

    def _generate_mock_variant(self, document: DocumentModel, persona: PersonaConfig, error_msg: str = "") -> VariantOutput:
        """Deterministic mock generator applying stylistic transformations locally."""
        styled_sections = []
        for sec in document.sections:
            paragraphs = sec.content.split("\n\n")
            transformed_paras = []
            for p in paragraphs:
                if persona.id == "senior_medical_editor":
                    p_styled = f"Clinical evidence indicates that {p.lower() if p else ''} Clear data underscores long-term health outcomes."
                elif persona.id == "scientific_explainer":
                    p_styled = f"To understand the underlying mechanism: {p} This demonstrates a clear cause-and-effect relationship."
                elif persona.id == "technical_writer":
                    p_styled = f"Operational protocol: {p} System requirements must adhere strictly to these parameters."
                elif persona.id == "conversational_expert":
                    p_styled = f"Here is what you need to know: {p} It is simpler than it looks once you get the hang of it."
                elif persona.id == "story_driven_educator":
                    p_styled = f"Consider a real-world scenario: {p} This practical context highlights the importance of execution."
                elif persona.id == "magazine_writer":
                    p_styled = f"In today's fast-moving environment, {p.lower() if p else ''} The strategic takeaway is undeniably compelling."
                elif persona.id == "evidence_first_writer":
                    p_styled = f"Empirical data confirms that {p.lower() if p else ''} Validated benchmarks substantiate these findings."
                elif persona.id == "demand_in_time_specialist":
                    p_styled = f"Considering contemporary reader demand and real-time context, {p.lower() if p else ''} Addressing these timely requirements ensures peak relevance today."
                else:
                    p_styled = f"{p}"
                transformed_paras.append(p_styled)

            styled_sections.append(
                Section(
                    heading=sec.heading,
                    level=sec.level,
                    content="\n\n".join(transformed_paras),
                    bullets=sec.bullets,
                    word_count=sum(len(tp.split()) for tp in transformed_paras)
                )
            )

        faqs = [
            FAQItem(
                question=f.question,
                answer=f"[{persona.name} Perspective] {f.answer}",
                line_count=f.line_count,
                word_count=len(f.answer.split()) + 3
            )
            for f in document.faqs
        ]

        raw_parts = [f"# {document.title}"]
        for s in styled_sections:
            raw_parts.append(f"## {s.heading}\n{s.content}")
        raw_text = "\n\n".join(raw_parts)

        return VariantOutput(
            persona_id=persona.id,
            persona_name=persona.name,
            title=document.title,
            sections=styled_sections,
            faqs=faqs,
            raw_text=raw_text,
            word_count=len(raw_text.split())
        )

    def _parse_generated_text(self, raw_text: str, persona: PersonaConfig, document: DocumentModel) -> VariantOutput:
        """Parse raw LLM markdown output into structured VariantOutput."""
        # Simple parser for generated markdown
        sections = []
        current_heading = "Introduction"
        current_paras = []
        for line in raw_text.splitlines():
            if line.startswith("## "):
                if current_paras:
                    sections.append(Section(heading=current_heading, level=2, content="\n\n".join(current_paras), word_count=sum(len(p.split()) for p in current_paras)))
                    current_paras = []
                current_heading = line.replace("## ", "").strip()
            elif line.strip() and not line.startswith("# "):
                current_paras.append(line.strip())

        if current_paras:
            sections.append(Section(heading=current_heading, level=2, content="\n\n".join(current_paras), word_count=sum(len(p.split()) for p in current_paras)))

        return VariantOutput(
            persona_id=persona.id,
            persona_name=persona.name,
            title=document.title,
            sections=sections or document.sections,
            faqs=document.faqs,
            raw_text=raw_text,
            word_count=len(raw_text.split())
        )
