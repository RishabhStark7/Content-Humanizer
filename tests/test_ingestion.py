"""Unit tests for document parsers."""

import unittest
from src.ingestion.router import parse_document


class TestIngestion(unittest.TestCase):
    def test_markdown_parser(self):
        md_content = """# Test Title

## Introduction
This is a test paragraph for markdown parsing.

- Point 1
- Point 2

## Frequently Asked Questions (FAQs)

### What is this?
This is a test question answer. It contains three lines of explanation for testing purposes. It ensures structural validity.
"""
        doc = parse_document(md_content)
        self.assertEqual(doc.title, "Test Title")
        self.assertGreaterEqual(len(doc.sections), 1)
        self.assertEqual(doc.original_format, "markdown")
        self.assertGreater(doc.total_word_count, 0)

    def test_text_parser(self):
        txt_content = """Test Text Title

Section One
This is plain text content. It should parse into sections properly.
"""
        doc = parse_document(txt_content)
        self.assertIsNotNone(doc.title)
        self.assertGreater(doc.total_word_count, 0)


if __name__ == "__main__":
    unittest.main()
