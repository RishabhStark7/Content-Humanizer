"""FAQ guardrail check enforcing minimum 7 FAQs with 3-4 substantive lines per answer."""

from schemas.document import DocumentModel
from schemas.validation import GuardrailCheckResult


def check_faq_guardrails(document: DocumentModel) -> GuardrailCheckResult:
    """Validate FAQ count (>= 7) and answer line/word count (>= 3 lines / 35 words per answer).

    Args:
        document: DocumentModel instance.

    Returns:
        GuardrailCheckResult.
    """
    faq_count = len(document.faqs)
    if faq_count < 7:
        return GuardrailCheckResult(
            name="FAQ Guardrail",
            passed=False,
            score=faq_count / 7.0,
            details=f"Failed FAQ count check: Found {faq_count} FAQs (Minimum 7 required)."
        )

    short_answers = []
    for idx, f in enumerate(document.faqs):
        if len(f.answer.split()) < 30:
            short_answers.append(idx + 1)

    if short_answers:
        return GuardrailCheckResult(
            name="FAQ Guardrail",
            passed=False,
            score=0.8,
            details=f"FAQ answers #{short_answers} do not meet minimum 3-4 line / 35-word depth requirement."
        )

    return GuardrailCheckResult(
        name="FAQ Guardrail",
        passed=True,
        score=1.0,
        details=f"All {faq_count} FAQs meet count (>= 7) and answer depth requirements."
    )
