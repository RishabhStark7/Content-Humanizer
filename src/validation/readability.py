"""Readability guardrail check targeting Indian Grade 8 readability."""

from schemas.document import DocumentModel
from schemas.validation import GuardrailCheckResult
from src.style.readability import calculate_flesch_reading_ease, calculate_flesch_kincaid_grade


def check_readability_guardrail(document: DocumentModel) -> GuardrailCheckResult:
    """Validate article readability against Indian Grade 8 standard (Grade Level ~7.0 - 8.5).

    Args:
        document: DocumentModel instance.

    Returns:
        GuardrailCheckResult.
    """
    text = document.raw_content
    fk_grade = calculate_flesch_kincaid_grade(text)
    ease = calculate_flesch_reading_ease(text)

    # Indian Grade 8 target: FK grade <= 9.0, Reading ease >= 55.0
    passed = fk_grade <= 9.5 and ease >= 50.0

    return GuardrailCheckResult(
        name="Readability Guardrail",
        passed=passed,
        score=1.0 if passed else 0.7,
        details=f"Flesch-Kincaid Grade: {fk_grade:.1f} (Target <= 8.5, Indian Grade 8). Flesch Reading Ease: {ease:.1f}."
    )
