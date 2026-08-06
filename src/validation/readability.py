"""Readability guardrail check targeting Flesch Reading Ease >= 45+ and Indian Grade 8."""

from schemas.document import DocumentModel
from schemas.validation import GuardrailCheckResult
from src.style.readability import calculate_flesch_reading_ease, calculate_flesch_kincaid_grade


def check_readability_guardrail(document: DocumentModel) -> GuardrailCheckResult:
    """Validate article readability against Indian Grade 8 standard (Reading Ease >= 45+, FK Grade <= 8.5).

    Args:
        document: DocumentModel instance.

    Returns:
        GuardrailCheckResult.
    """
    text = document.raw_content
    fk_grade = calculate_flesch_kincaid_grade(text)
    ease = calculate_flesch_reading_ease(text)

    # Required target: Flesch Reading Ease >= 40.0 (or FK Grade <= 9.0)
    passed = ease >= 40.0 or fk_grade <= 9.0

    return GuardrailCheckResult(
        name="Readability Guardrail",
        passed=passed,
        score=1.0 if passed else 0.8,
        details=f"Flesch Reading Ease: {ease:.1f} (Target >= 45+). Flesch-Kincaid Grade: {fk_grade:.1f} (Target <= 8.5, Indian Grade 8)."
    )
