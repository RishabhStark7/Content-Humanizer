"""Word count guardrail check."""

from schemas.document import DocumentModel
from schemas.validation import GuardrailCheckResult


def check_word_count(
    document: DocumentModel,
    target_count: int = 1500,
    tolerance: int = 100
) -> GuardrailCheckResult:
    """Validate article word count against target (±100 words, FAQs excluded if specified).

    Args:
        document: DocumentModel instance.
        target_count: Targeted word count.
        tolerance: Allowed deviation (+/- words).

    Returns:
        GuardrailCheckResult instance.
    """
    article_words = sum(s.word_count for s in document.sections)
    min_allowed = max(100, target_count - tolerance)
    max_allowed = target_count + tolerance

    passed = min_allowed <= article_words <= max_allowed
    details = f"Article word count: {article_words} words (Target: {target_count} ± {tolerance}). Allowed range: [{min_allowed}, {max_allowed}]."

    return GuardrailCheckResult(
        name="Word Count Guardrail",
        passed=passed,
        score=1.0 if passed else max(0.0, 1.0 - (abs(article_words - target_count) / target_count)),
        details=details
    )
