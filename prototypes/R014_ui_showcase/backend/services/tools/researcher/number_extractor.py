# =============================================================================
# AGENTX Number Extractor Module
# =============================================================================
# Extracts structured numbers from research documents for chart/table data
# =============================================================================

from typing import Any

import json
import logging

import dspy
from services.tools.hydrators.signatures import ExtractDocumentNumbers
from services.tools.researcher.regex_fallback import extract_numbers_with_regex

logger = logging.getLogger(__name__)


class NumberExtractorModule(dspy.Module):
    """Extract structured numbers from research documents.

    Processes raw research documents and extracts numerical data
    with labels, values, units, and source citations.
    """

    def __init__(self, max_documents: int = 10):
        super().__init__()
        self.extractor = dspy.ChainOfThought(ExtractDocumentNumbers)
        self.max_documents = max_documents

    def forward(self, raw_data: list) -> dict[str, Any]:
        """Extract numbers from research documents.

        Args:
            raw_data: List of document dicts with title, content, url

        Returns:
            Dict with extracted_numbers array and metadata
        """
        extracted_numbers = []
        processed_docs = raw_data[: self.max_documents]

        for index, doc in enumerate(processed_docs):
            content = doc.get("content", "")[:2000]
            title = doc.get("title", "")
            url = doc.get("url", "")

            if not content or len(content) < 50:
                continue

            result = self._extract_with_llm(content, title, url, index)

            if result:
                extracted_numbers.extend(result)
            else:
                extracted_numbers.extend(
                    extract_numbers_with_regex(content, title, url, index)
                )

        extracted_numbers = self._deduplicate(extracted_numbers)

        return {
            "extracted_numbers": extracted_numbers,
            "metadata": {
                "total_numbers": len(extracted_numbers),
                "documents_processed": len(processed_docs),
                "extraction_method": "llm",
                "has_year_data": any(n.get("year") for n in extracted_numbers),
            },
        }

    def _extract_with_llm(
        self, content: str, title: str, url: str, doc_index: int
    ) -> list:
        """Extract numbers using LLM.

        Args:
            content: Document content text
            title: Document title
            url: Document URL
            doc_index: Document index in raw_data

        Returns:
            List of extracted number dicts
        """
        try:
            result = self.extractor(document_text=content, document_title=title)

            numbers_str = getattr(result, "structured_numbers", "")
            if isinstance(numbers_str, str):
                numbers = json.loads(numbers_str)
            elif isinstance(numbers_str, list):
                numbers = numbers_str
            else:
                return []

            for num in numbers:
                num["source_doc"] = doc_index
                num["source_title"] = title
                num["url"] = url

            return numbers

        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            logger.warning(f"LLM extraction failed: {e}")
            return []

    def _deduplicate(self, numbers: list) -> list:
        """Remove duplicate numbers based on label+value+year."""
        seen = set()
        unique = []

        for num in numbers:
            key = (num.get("label"), num.get("value"), num.get("year"))
            if key not in seen:
                seen.add(key)
                unique.append(num)

        return unique
