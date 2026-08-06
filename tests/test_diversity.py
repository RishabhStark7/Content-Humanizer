"""Unit tests for diversity metrics and filtering."""

import unittest
from schemas.variant import VariantOutput
from src.diversity.filter import filter_most_diverse_variants
from src.diversity.similarity import calculate_jaccard_similarity


class TestDiversity(unittest.TestCase):
    def test_similarity_math(self):
        sim = calculate_jaccard_similarity("The quick brown fox", "The quick brown dog")
        self.assertTrue(0.5 <= sim < 1.0)

    def test_diversity_filter_10_to_7(self):
        variants = [
            VariantOutput(persona_id=f"persona_{i}", persona_name=f"Persona {i}", title="Title", raw_text=f"Text content variation {i} with unique words {i*10}")
            for i in range(10)
        ]
        retained, report = filter_most_diverse_variants(variants, retain_count=7)
        self.assertEqual(len(retained), 7)
        self.assertEqual(report.retained_count, 7)
        self.assertEqual(report.discarded_count, 3)


if __name__ == "__main__":
    unittest.main()
