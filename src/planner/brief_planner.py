"""Brief planner that converts ContentBriefModel into structured document plan."""

from schemas.brief import ContentBriefModel
from schemas.document import DocumentModel, Section, FAQItem


def prepare_plan_from_brief(brief: ContentBriefModel) -> DocumentModel:
    """Transform a content brief into an initial structured DocumentModel baseline.

    Args:
        brief: ContentBriefModel instance.

    Returns:
        Structured DocumentModel baseline for generation.
    """
    title = brief.topic.title()
    sections = [
        Section(
            heading=f"Introduction to {brief.topic}",
            level=2,
            content=f"An in-depth overview covering {brief.topic} tailored for {brief.target_audience}. Objective: {brief.objective}.",
            bullets=brief.keywords[:3],
            word_count=200
        ),
        Section(
            heading=f"Core Concepts and Key Insights",
            level=2,
            content=f"Detailed technical and practical breakdown of {brief.topic}.",
            bullets=brief.geo_aeo_entities,
            word_count=500
        ),
        Section(
            heading=f"Step-by-Step Practical Guidance",
            level=2,
            content=f"Actionable recommendations and decision support for {brief.target_audience}.",
            bullets=[],
            word_count=400
        ),
        Section(
            heading=f"Conclusion and Best Practices",
            level=2,
            content=f"Summary of key takeaways and actionable conclusions.",
            bullets=[],
            word_count=150
        ),
    ]

    faqs = [
        FAQItem(
            question=f"What is the significance of {brief.topic}?",
            answer=f"{brief.topic} plays a pivotal role in modern contexts by establishing clear benchmarks and practical guidelines. Understanding its core principles allows practitioners to optimize outcomes efficiently while mitigating common operational risks.",
            line_count=3,
            word_count=38
        ),
        FAQItem(
            question=f"Who benefits most from applying these principles?",
            answer=f"Primary beneficiaries include {brief.target_audience} who seek structured, evidence-based solutions. Implementing these recommendations directly improves quality, consistency, and long-term performance across varied applications.",
            line_count=3,
            word_count=35
        ),
        FAQItem(
            question=f"How does this approach compare to traditional methods?",
            answer=f"Traditional approaches often rely on manual, repetitive steps that increase variability. In contrast, this structured method incorporates automated validation, clear heading hierarchies, and rigorous editorial guardrails for consistent excellence.",
            line_count=3,
            word_count=37
        ),
        FAQItem(
            question=f"What are the initial steps to get started?",
            answer=f"Getting started requires assessing current workflows, defining objective metrics, and establishing clear target parameters. Begin with foundational components before scaling across broader organizational contexts.",
            line_count=3,
            word_count=36
        ),
        FAQItem(
            question=f"What common mistakes should be avoided?",
            answer=f"Key pitfalls include skipping foundational validation, ignoring keyword coverage, and over-relying on unrefined draft outputs. Maintaining strict editorial oversight ensures accuracy and readability throughout.",
            line_count=3,
            word_count=36
        ),
        FAQItem(
            question=f"How can progress and accuracy be measured effectively?",
            answer=f"Evaluate progress through standardized readability scores, structural heading checks, and target word count compliance. Regular auditing maintains high standards and supports continuous refinement.",
            line_count=3,
            word_count=35
        ),
        FAQItem(
            question=f"Where can additional resources and guidance be found?",
            answer=f"Consult technical documentation, peer-reviewed benchmarks, and official brand guidelines for comprehensive reference material. Continuous learning and adherence to established frameworks ensure optimal results.",
            line_count=3,
            word_count=36
        ),
    ]

    total_words = sum(s.word_count for s in sections) + sum(f.word_count for f in faqs)

    return DocumentModel(
        title=title,
        metadata={
            "objective": brief.objective,
            "audience": brief.target_audience,
            "tone": brief.tone,
            "keywords": brief.keywords,
            "target_word_count": brief.target_word_count,
        },
        sections=sections,
        faqs=faqs,
        original_format="brief",
        total_word_count=total_words,
        raw_content=f"# {title}\n\n" + "\n\n".join(f"## {s.heading}\n{s.content}" for s in sections)
    )
