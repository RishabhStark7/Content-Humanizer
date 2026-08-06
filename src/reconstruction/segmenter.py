"""Sentence tokenizer and clause segmenter."""

import re
from typing import List


def segment_sentences(text: str) -> List[str]:
    """Split paragraph text into individual sentences.

    Args:
        text: Paragraph or section body text.

    Returns:
        List of trimmed sentence strings.
    """
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def extract_clauses(sentence: str) -> List[str]:
    """Split long sentence into constituent clause phrases on commas, semicolons, and conjunctions."""
    clauses = re.split(r"[,;]\s+|\s+(?:and|but|while|whereas|although)\s+", sentence)
    return [c.strip() for c in clauses if c.strip()]
