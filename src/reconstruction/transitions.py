"""Deterministic transition improver replacing formulaic AI starters with natural human transitions."""

import re

REPETITIVE_STARTERS = [
    r"^Furthermore,\s*",
    r"^In conclusion,\s*",
    r"^Moreover,\s*",
    r"^It is important to note that\s*",
    r"^Additionally,\s*",
    r"^Consequently,\s*",
    r"^Overall,\s*",
    r"^In summary,\s*",
]

NATURAL_TRANSITIONS = [
    "Notably,",
    "Beyond this,",
    "In practice,",
    "Crucially,",
    "As a result,",
    "At the same time,",
    "To understand this better,",
    "For instance,",
]


def improve_sentence_transition(sentence: str, index: int) -> str:
    """Clean robotic AI transitions and inject varied natural transitions.

    Args:
        sentence: Input sentence string.
        index: Index of sentence in paragraph.

    Returns:
        Sentence with natural transition phrasing.
    """
    cleaned = sentence
    for pattern in REPETITIVE_STARTERS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    # Capitalize first letter if stripped
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]

    # Optionally add natural transition to second/third sentence if appropriate
    if index == 1 and not cleaned.startswith(tuple(NATURAL_TRANSITIONS)):
        # Keep clean without over-injecting
        pass

    return cleaned
