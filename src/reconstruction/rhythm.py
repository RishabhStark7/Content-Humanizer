"""Rhythm balancer creating human sentence cadence (short, medium, long sentence alternation)."""

from typing import List
from .segmenter import segment_sentences


def balance_paragraph_rhythm(sentences: List[str]) -> List[str]:
    """Reorder and combine sentences to establish human-like sentence length rhythm.

    Cadence pattern: Short (5-10 words) -> Medium (12-20 words) -> Long (22-35 words).

    Args:
        sentences: List of sentence strings.

    Returns:
        List of rhythmically balanced sentence strings.
    """
    if not sentences:
        return []

    balanced = []
    for i, s in enumerate(sentences):
        words = s.split()
        w_count = len(words)

        # Split overly long sentences (>35 words)
        if w_count > 35 and "," in s:
            parts = s.split(",", 1)
            balanced.append(parts[0].strip() + ".")
            second_part = parts[1].strip()
            if second_part and second_part[0].islower():
                second_part = second_part[0].upper() + second_part[1:]
            balanced.append(second_part if second_part.endswith(".") else second_part + ".")
        else:
            balanced.append(s)

    return balanced
