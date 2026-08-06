"""Unit tests for editorial guardrail validation layer."""

import unittest
from schemas.document import DocumentModel, Section, FAQItem
from src.validation.engine import validate_article


class TestValidation(unittest.TestCase):
    def test_validation_engine(self):
        faqs = [
            FAQItem(
                question=f"Question #{i}?",
                answer="Answer line one explaining the core medical or technical mechanism in full detail.\nAnswer line two providing essential supporting data points, examples, and verified evidence.\nAnswer line three confirming practical execution steps, decision guidelines, and long-term publication-ready best practices for readers.",
                line_count=3,
                word_count=36
            )
            for i in range(7)
        ]

        doc = DocumentModel(
            title="Comprehensive Health Guide",
            sections=[
                Section(heading="Introduction", level=2, content="This is a comprehensive overview of preventive health. It covers primary interventions and clinical evidence.", word_count=200),
                Section(heading="Key Interventions", level=2, content="Detailed breakdown of health monitoring protocols.", word_count=300)
            ],
            faqs=faqs,
            total_word_count=500,
            raw_content="# Comprehensive Health Guide\n\n## Introduction\nContent here.\n\n## Key Interventions\nContent here."
        )

        report = validate_article(doc, target_word_count=500)
        self.assertTrue(report.faq_check.passed)
        self.assertTrue(report.heading_hierarchy_check.passed)


if __name__ == "__main__":
    unittest.main()
