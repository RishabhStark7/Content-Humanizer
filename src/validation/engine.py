"""Consolidated validation engine running all guardrail checks."""

from schemas.document import DocumentModel
from schemas.validation import ValidationReport, GuardrailCheckResult
from src.style.cliche_cleaner import BANNED_CLICHES
from src.style.readability import calculate_flesch_kincaid_grade, calculate_flesch_reading_ease
from .word_count import check_word_count
from .readability import check_readability_guardrail
from .faq_checker import check_faq_guardrails
from .seo import check_seo_guardrails
from .geo_aeo import check_geo_aeo_guardrails


def validate_article(
    document: DocumentModel,
    target_word_count: int = 1500
) -> ValidationReport:
    """Run all guardrail checks against the synthesized document.

    Args:
        document: Synthesized DocumentModel.
        target_word_count: Target word count from brief or original document.

    Returns:
        ValidationReport instance.
    """
    word_check = check_word_count(document, target_count=target_word_count)
    readability_check = check_readability_guardrail(document)
    faq_check = check_faq_guardrails(document)
    seo_check = check_seo_guardrails(document)
    geo_aeo_check = check_geo_aeo_guardrails(document)

    # Heading hierarchy check
    h_levels = [s.level for s in document.sections]
    hierarchy_passed = True
    for i in range(len(h_levels) - 1):
        if h_levels[i+1] > h_levels[i] + 1:
            hierarchy_passed = False
            break
    heading_check = GuardrailCheckResult(
        name="Heading Hierarchy Guardrail",
        passed=hierarchy_passed,
        score=1.0 if hierarchy_passed else 0.5,
        details="Strict H1 -> H2 -> H3 hierarchy preserved." if hierarchy_passed else "Heading level skipped (e.g. H1 to H3)."
    )

    # Cliche check
    text_lower = document.raw_content.lower()
    found_cliches = [c.replace(r"\b", "") for c in BANNED_CLICHES if c.replace(r"\b", "") in text_lower]
    cliche_passed = len(found_cliches) == 0
    cliche_check = GuardrailCheckResult(
        name="AI Cliché Guardrail",
        passed=cliche_passed,
        score=1.0 if cliche_passed else max(0.0, 1.0 - (len(found_cliches) * 0.1)),
        details="No banned AI clichés detected." if cliche_passed else f"Found AI clichés: {found_cliches}."
    )

    all_checks = [word_check, readability_check, faq_check, seo_check, geo_aeo_check, heading_check, cliche_check]
    passed = all(c.passed for c in all_checks)

    errors = [c.details for c in all_checks if not c.passed]

    return ValidationReport(
        passed=passed,
        word_count_check=word_check,
        readability_check=readability_check,
        faq_check=faq_check,
        heading_hierarchy_check=heading_check,
        seo_check=seo_check,
        geo_aeo_check=geo_aeo_check,
        cliche_check=cliche_check,
        metrics={
            "flesch_reading_ease": calculate_flesch_reading_ease(document.raw_content),
            "flesch_kincaid_grade": calculate_flesch_kincaid_grade(document.raw_content),
            "total_word_count": document.total_word_count,
            "faq_count": len(document.faqs),
            "section_count": len(document.sections),
        },
        errors=errors,
        warnings=[]
    )
