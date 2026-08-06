"""Pairwise similarity metrics calculation."""

import re
from typing import List, Set
from rapidfuzz import distance


def get_words(text: str) -> Set[str]:
    """Tokenize text into lower-case word set."""
    return set(re.findall(r"\b\w+\b", text.lower()))


def calculate_jaccard_similarity(text1: str, text2: str) -> float:
    """Calculate Jaccard similarity between two texts (0.0 = completely distinct, 1.0 = identical)."""
    set1 = get_words(text1)
    set2 = get_words(text2)
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0


def calculate_lexical_similarity(text1: str, text2: str) -> float:
    """Calculate normalized Levenshtein similarity distance."""
    if not text1 or not text2:
        return 0.0
    return distance.Levenshtein.normalized_similarity(text1, text2)


def calculate_structural_similarity(len_list1: List[int], len_list2: List[int]) -> float:
    """Compare section length distributions."""
    if not len_list1 or not len_list2:
        return 0.0
    min_len = min(len(len_list1), len(len_list2))
    if min_len == 0:
        return 0.0
    diffs = [abs(len_list1[i] - len_list2[i]) / max(len_list1[i], len_list2[i], 1) for i in range(min_len)]
    avg_diff = sum(diffs) / len(diffs)
    return max(0.0, 1.0 - avg_diff)
