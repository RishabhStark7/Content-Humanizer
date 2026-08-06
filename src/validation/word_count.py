"""Word count guardrail check excluding FAQs per specification."""

from schemas.document import DocumentModel
from schemas.validation import GuardrailCheckResult


def check_word_count(
    document: DocumentModel,
    target_count: int = 1215,
    tolerance: int = 100
) -> GuardrailCheckResult:
    """Validate body word count against target (±100 words, FAQs excluded per spec).

    Args:
        document: DocumentModel instance.
        target_count: Targeted body word count.
        tolerance: Allowed deviation (+/- words).

    Returns:
        GuardrailCheckResult instance.
    """
    # Calculate body word count excluding FAQs
    body_words = sum(s.word_count for s in document.sections if "faq" not in s.heading.lower())

    # Determine effective body target count
    if 900 <= target_count <= 1400:
        effective_target = target_count
    elif target_count > 1400:
        effective_target = int(target_count * 0.65)
    else:
        effective_target = 1200

    min_allowed = max(100, effective_target - tolerance)
    max_allowed = effective_target + tolerance

    passed = min_allowed <= body_words <= max_allowed
    details = f"Article body word count (FAQs excluded): {body_words} words (Target: {effective_target} ± {tolerance}). Allowed range: [{min_allowed}, {max_allowed}]."

    return GuardrailCheckResult(
        name="Word Count Guardrail",
        passed=passed,
        score=1.0 if passed else max(0.0, 1.0 - (abs(body_words - effective_target) / effective_target)),
        details=details
    )
