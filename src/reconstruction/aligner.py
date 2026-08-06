"""Section alignment mapping matching sections across the 7 retained variants."""

from typing import List, Dict
from schemas.variant import VariantOutput
from schemas.document import Section


def align_sections_across_variants(variants: List[VariantOutput]) -> Dict[str, List[Section]]:
    """Group section contents from all 7 variants by normalized heading name.

    Args:
        variants: List of 7 retained VariantOutput items.

    Returns:
        Dictionary mapping normalized heading -> List of Section objects from each variant.
    """
    aligned: Dict[str, List[Section]] = {}
    for v in variants:
        for sec in v.sections:
            norm_heading = sec.heading.strip()
            if norm_heading not in aligned:
                aligned[norm_heading] = []
            aligned[norm_heading].append(sec)
    return aligned
