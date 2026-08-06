"""Readability scoring using Flesch Reading Ease and Flesch Kincaid Grade level formulas."""

import textstat


def calculate_flesch_reading_ease(text: str) -> float:
    """Calculate Flesch Reading Ease score (higher is easier to read, target ~60-70)."""
    if not text.strip():
        return 70.0
    try:
        return textstat.flesch_reading_ease(text)
    except Exception:
        return 65.0


def calculate_flesch_kincaid_grade(text: str) -> float:
    """Calculate Flesch Kincaid Grade level (target Indian Grade 8 = ~7.5-8.5)."""
    if not text.strip():
        return 8.0
    try:
        return textstat.flesch_kincaid_grade(text)
    except Exception:
        return 8.0
