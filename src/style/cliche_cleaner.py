"""AI cliché cleaner removing overused AI filler words."""

import re

BANNED_CLICHES = [
    r"\bdelve\b",
    r"\btapestry\b",
    r"\btestament\b",
    r"\bpivotal\b",
    r"\bunleash\b",
    r"\blandscape\b",
    r"\brealm\b",
    r"\bbeacon\b",
    r"\bgame-changer\b",
    r"\bparamount\b",
    r"\bfostering\b",
    r"\bholistic\b",
]

REPLACEMENTS = {
    "delve": "examine",
    "tapestry": "combination",
    "testament": "proof",
    "pivotal": "important",
    "unleash": "release",
    "landscape": "field",
    "realm": "area",
    "beacon": "model",
    "game-changer": "major advance",
    "paramount": "key",
    "fostering": "building",
    "holistic": "complete",
}


def clean_ai_cliches(text: str) -> str:
    """Replace common AI clichés with clear human words.

    Args:
        text: Input article text.

    Returns:
        Cleaned text with AI clichés removed.
    """
    cleaned = text
    for word, replacement in REPLACEMENTS.items():
        pattern = re.compile(rf"\b{word}\b", re.IGNORECASE)
        cleaned = pattern.sub(replacement, cleaned)
    return cleaned
