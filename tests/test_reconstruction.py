"""Unit tests for Local Human Reconstruction Engine."""

import unittest
from schemas.document import DocumentModel, Section, FAQItem
from schemas.variant import VariantOutput
from src.reconstruction.engine import reconstruct_article
from src.reconstruction.transitions import improve_sentence_transition


class TestReconstruction(unittest.TestCase):
    def test_transition_cleanup(self):
        s = "Furthermore, this method provides great results."
        cleaned = improve_sentence_transition(s, index=0)
        self.assertFalse(cleaned.startswith("Furthermore"))

    def test_reconstruction_engine_synthesis(self):
        base_doc = DocumentModel(
            title="Test Article",
            sections=[Section(heading="Intro", level=2, content="Initial text.", word_count=10)],
            faqs=[FAQItem(question="Q1?", answer="Line 1\nLine 2\nLine 3 of answer with over thirty five words for proper validation.", line_count=3, word_count=36)],
            total_word_count=50
        )

        retained = [
            VariantOutput(
                persona_id=f"p_{i}",
                persona_name=f"P {i}",
                title="Test Article",
                sections=[Section(heading="Intro", level=2, content=f"Persona {i} detailed explanation of the core concept. It provides clear insights.", word_count=20)],
                faqs=base_doc.faqs,
                raw_text="raw"
            )
            for i in range(7)
        ]

        reconstructed = reconstruct_article(retained, base_doc)
        self.assertEqual(reconstructed.title, "Test Article")
        self.assertGreaterEqual(len(reconstructed.sections), 1)
        self.assertGreaterEqual(len(reconstructed.faqs), 7)


if __name__ == "__main__":
    unittest.main()
