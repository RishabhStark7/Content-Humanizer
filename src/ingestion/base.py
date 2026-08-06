"""Base abstract parser class for document ingestion."""

from abc import ABC, abstractmethod
from typing import Union
from pathlib import Path
from schemas.document import DocumentModel


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, file_path_or_content: Union[str, Path]) -> DocumentModel:
        """Parse raw file or content into a structured DocumentModel.

        Args:
            file_path_or_content: File path or raw text string.

        Returns:
            DocumentModel containing title, hierarchy, sections, and FAQs.
        """
        pass
