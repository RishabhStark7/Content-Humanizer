"""Diversity filter evaluating pairwise variant similarity and discarding top 3 redundant variants."""

from typing import List, Tuple, Dict
from schemas.variant import VariantOutput
from schemas.diversity import DiversityReport
from .similarity import calculate_jaccard_similarity, calculate_lexical_similarity, calculate_structural_similarity


def filter_most_diverse_variants(
    variants: List[VariantOutput],
    retain_count: int = 7
) -> Tuple[List[VariantOutput], DiversityReport]:
    """Analyze 10 generated variants, compute pairwise similarity, discard the 3 most redundant, and retain 7.

    Args:
        variants: List of 10 VariantOutput items.
        retain_count: Number of variants to retain (default 7).

    Returns:
        Tuple containing (7 Retained VariantOutput list, DiversityReport).
    """
    n = len(variants)
    if n <= retain_count:
        report = DiversityReport(
            total_generated=n,
            retained_count=n,
            discarded_count=0,
            retained_persona_ids=[v.persona_id for v in variants],
            discarded_persona_ids=[],
            similarity_matrix={},
            diversity_scores={v.persona_id: 1.0 for v in variants}
        )
        return variants, report

    matrix: Dict[str, Dict[str, float]] = {}
    average_similarity: Dict[str, float] = {}

    for i in range(n):
        v1 = variants[i]
        matrix[v1.persona_id] = {}
        total_sim = 0.0

        for j in range(n):
            v2 = variants[j]
            if i == j:
                matrix[v1.persona_id][v2.persona_id] = 1.0
                continue

            jaccard = calculate_jaccard_similarity(v1.raw_text, v2.raw_text)
            lexical = calculate_lexical_similarity(v1.raw_text[:1000], v2.raw_text[:1000])
            sec_lens1 = [s.word_count for s in v1.sections]
            sec_lens2 = [s.word_count for s in v2.sections]
            structural = calculate_structural_similarity(sec_lens1, sec_lens2)

            composite_sim = (jaccard * 0.4) + (lexical * 0.4) + (structural * 0.2)
            matrix[v1.persona_id][v2.persona_id] = composite_sim
            total_sim += composite_sim

        average_similarity[v1.persona_id] = total_sim / (n - 1)

    # Sort variants by average similarity ascending (least similar / most diverse first)
    sorted_personas = sorted(average_similarity.keys(), key=lambda p_id: average_similarity[p_id])

    retained_ids = sorted_personas[:retain_count]
    discarded_ids = sorted_personas[retain_count:]

    retained_variants = [v for v in variants if v.persona_id in retained_ids]

    diversity_scores = {p_id: round(1.0 - sim, 4) for p_id, sim in average_similarity.items()}

    report = DiversityReport(
        total_generated=n,
        retained_count=len(retained_variants),
        discarded_count=len(discarded_ids),
        retained_persona_ids=retained_ids,
        discarded_persona_ids=discarded_ids,
        similarity_matrix=matrix,
        diversity_scores=diversity_scores
    )

    return retained_variants, report
