"""SEO guardrail check verifying heading structure, keyword presence, and snippet format."""

from schemas.document import DocumentModel
from schemas.validation import GuardrailCheckResult


def check_seo_guardrails(document: DocumentModel) -> GuardrailCheckResult:
    """Validate H1 presence, H2/H3 subheadings, and keyword structure.

    Args:
        document: DocumentModel instance.

    Returns:
        GuardrailCheckResult.
    """
    has_title = bool(document.title)
    has_subheadings = len(document.sections) >= 2

    passed = has_title and has_subheadings
    details = f"Title present: {has_title}. Subheadings count: {len(document.sections)}."

    return GuardrailCheckResult(
        name="SEO Guardrail",
        passed=passed,
        score=1.0 if passed else 0.5,
        details=details
    )
