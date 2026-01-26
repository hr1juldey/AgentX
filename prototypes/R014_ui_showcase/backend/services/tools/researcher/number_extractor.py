# =============================================================================
# AGENTX Number Extractor Module
# =============================================================================
# Extracts structured numbers from research documents for chart/table data
# =============================================================================

from typing import Any

import logging

import dspy
from services.tools.hydrators.chart_signatures import ExtractDocumentNumbers

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

    def forward(self, raw_data: list, query: str = "") -> dict[str, Any]:
        """Extract numbers from research documents.

        Args:
            raw_data: List of document dicts with title, content, url
            query: Research query for context (optional)

        Returns:
            Dict with extracted_numbers array and metadata
        """
        from services.tools.researcher.llm_number_handler import (
            extract_numbers_from_document,
        )
        from services.tools.researcher.regex_fallback import extract_numbers_with_regex

        extracted_numbers = []
        processed_docs = raw_data[: self.max_documents]

        logger.info(
            f"[NUMBER_EXTRACTOR] Processing {len(raw_data)} documents (max: {self.max_documents})"
        )

        for index, doc in enumerate(processed_docs):
            # Prioritize full_content if available, fallback to snippet
            content = (doc.get("full_content", "") or doc.get("content", ""))[:5000]
            title = doc.get("title", "")
            url = doc.get("url", "")

            if not content or len(content) < 50:
                logger.warning(
                    f"[NUMBER_EXTRACTOR] Skipped doc {index}: content_len={len(content)}",
                )
                continue

            # Try LLM extraction
            numbers = extract_numbers_from_document(
                extractor=self.extractor,
                content=content,
                title=title,
                url=url,
                doc_index=index,
                query=query,
            )

            if numbers:
                logger.info(f"[NUMBER_EXTRACTOR] LLM extracted {len(numbers)} numbers")
                extracted_numbers.extend(numbers)
            else:
                # LLM failed, use regex fallback
                regex_result = extract_numbers_with_regex(content, title, url, index)
                logger.info(
                    f"[NUMBER_EXTRACTOR] Regex extracted {len(regex_result)} numbers"
                )
                extracted_numbers.extend(regex_result)

        # Deduplicate and return
        extracted_numbers = self._deduplicate(extracted_numbers)
        logger.info(f"[NUMBER_EXTRACTOR] Total after dedup: {len(extracted_numbers)}")

        return {
            "extracted_numbers": extracted_numbers,
            "metadata": {
                "total_numbers": len(extracted_numbers),
                "documents_processed": len(processed_docs),
                "extraction_method": "llm",
                "has_year_data": any(n.get("year") for n in extracted_numbers),
            },
        }

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
