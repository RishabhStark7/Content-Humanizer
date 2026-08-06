"""Banned AI cliché and robotic transition cleaner."""

import re

BANNED_AI_CLICHES = [
    # Explicitly forbidden transitions and AI habits
    "this is why",
    "together, these",
    "these measures",
    "these processes",
    "helps maintain",
    "helps support",
    "designed to",
    "throughout the journey",
    "plays an important role",
    "in addition",
    "furthermore",
    "moreover",
    "it starts with",
    "it continues through",
    "provides transparency",
    "gives visibility",
    # General AI fluff words
    "delve",
    "tapestry",
    "testament",
    "beacon",
    "vital role",
    "pivotal",
    "game-changer",
    "seamlessly",
    "paramount", "leverage", "robust", "synergy",
]

BANNED_CLICHES = BANNED_AI_CLICHES


def clean_ai_cliches(text: str) -> str:
    """Strip banned AI cliché transitions and robotic phrases from text.

    Args:
        text: Input string.

    Returns:
        Cleaned text string.
    """
    if not text:
        return text

    cleaned = text
    for cliché in BANNED_AI_CLICHES:
        pattern = re.compile(rf"\b{re.escape(cliché)}\b,?\s*", re.IGNORECASE)
        cleaned = pattern.sub("", cleaned)

    # Clean double spaces and leading spaces on lines
    cleaned = re.sub(r" +", " ", cleaned)
    cleaned = re.sub(r"\n +", "\n", cleaned)
    return cleaned.strip()
