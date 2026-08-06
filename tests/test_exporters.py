"""Unit tests for DOCX, Markdown, HTML, and JSON exporters."""

import unittest
from pathlib import Path
import tempfile
from schemas.document import DocumentModel, Section, FAQItem
from src.exporters.docx_exporter import export_to_docx
from src.exporters.md_exporter import export_to_markdown
from src.exporters.html_exporter import export_to_html
from src.exporters.json_exporter import export_to_json


class TestExporters(unittest.TestCase):
    def test_exporters_end_to_end(self):
        doc = DocumentModel(
            title="Export Test Title",
            sections=[Section(heading="Heading 1", level=2, content="Test section content", word_count=10)],
            faqs=[FAQItem(question="Q?", answer="Answer line 1\nLine 2\nLine 3", line_count=3, word_count=35)],
            total_word_count=45,
            raw_content="# Export Test Title"
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            docx_file = export_to_docx(doc, tmp_path / "test.docx")
            md_file = export_to_markdown(doc, tmp_path / "test.md")
            html_file = export_to_html(doc, tmp_path / "test.html")
            json_file = export_to_json(doc, tmp_path / "test.json")

            self.assertTrue(docx_file.exists())
            self.assertTrue(md_file.exists())
            self.assertTrue(html_file.exists())
            self.assertTrue(json_file.exists())


if __name__ == "__main__":
    unittest.main()
