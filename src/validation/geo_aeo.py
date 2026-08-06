"""GEO and AEO guardrail check for AI engine optimization and answer retrieval."""

from schemas.document import DocumentModel
from schemas.validation import GuardrailCheckResult


def check_geo_aeo_guardrails(document: DocumentModel) -> GuardrailCheckResult:
    """Validate presence of structured definitions, lists, and direct Q&A for AI engine retrieval.

    Args:
        document: DocumentModel instance.

    Returns:
        GuardrailCheckResult.
    """
    has_faqs = len(document.faqs) >= 7
    has_bullets = any(bool(s.bullets) for s in document.sections)

    passed = has_faqs or has_bullets
    details = f"Structured FAQs count: {len(document.faqs)}. Bullet lists present: {has_bullets}."

    return GuardrailCheckResult(
        name="GEO / AEO Guardrail",
        passed=passed,
        score=1.0 if passed else 0.6,
        details=details
    )
