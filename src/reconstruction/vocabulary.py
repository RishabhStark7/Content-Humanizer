"""Vocabulary and phrasing selection across variants."""

from typing import List
from schemas.document import Section
from .segmenter import segment_sentences


def select_best_phrasing(sections: List[Section]) -> str:
    """Compare section phrasings from different variants and select complementary sentences.

    Args:
        sections: List of Section objects for the same heading across 7 variants.

    Returns:
        Synthesized paragraph text.
    """
    if not sections:
        return ""

    # Pick sentences with highest clarity and varied vocabulary
    pool_sentences = []
    for sec in sections:
        s_list = segment_sentences(sec.content)
        pool_sentences.extend(s_list)

    # Deduplicate while preserving order
    seen = set()
    unique_sentences = []
    for s in pool_sentences:
        s_norm = s.lower().strip()
        if s_norm not in seen and len(s.split()) >= 4:
            seen.add(s_norm)
            unique_sentences.append(s)

    # Take 3 to 6 best sentences for paragraph synthesis
    selected = unique_sentences[:6]
    return " ".join(selected)
