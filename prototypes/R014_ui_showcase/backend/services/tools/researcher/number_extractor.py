# =============================================================================
# AGENTX Number Extractor Module
# =============================================================================
# Extracts structured numbers from research documents for chart/table data
# =============================================================================

from typing import Any

import json
import logging

import dspy
from services.tools.hydrators.chart_signatures import ExtractDocumentNumbers
from services.tools.researcher.number_extractor_utils import strip_markdown_wrapper
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

        logger.info(
            f"[NUMBER_EXTRACTOR] Processing {len(raw_data)} documents (max: {self.max_documents})"
        )

        for index, doc in enumerate(processed_docs):
            content = doc.get("content", "")[:2000]
            title = doc.get("title", "")
            url = doc.get("url", "")

            if not content or len(content) < 50:
                logger.warning(
                    f"[NUMBER_EXTRACTOR] Skipped doc {index}: content_len={len(content)}, title='{title[:50]}'"
                )
                continue

            result = self._extract_with_llm(content, title, url, index)

            if result:
                logger.info(
                    f"[NUMBER_EXTRACTOR] LLM extracted {len(result)} numbers from '{title[:50]}'"
                )
                extracted_numbers.extend(result)
            else:
                regex_result = extract_numbers_with_regex(content, title, url, index)
                logger.info(
                    f"[NUMBER_EXTRACTOR] Regex extracted {len(regex_result)} numbers from '{title[:50]}'"
                )
                extracted_numbers.extend(regex_result)

        logger.info(
            f"[NUMBER_EXTRACTOR] Total numbers before dedup: {len(extracted_numbers)}"
        )
        extracted_numbers = self._deduplicate(extracted_numbers)
        logger.info(
            f"[NUMBER_EXTRACTOR] Total numbers after dedup: {len(extracted_numbers)}"
        )

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
        result = None
        numbers_str = ""
        try:
            # Log input content for debugging
            logger.info(
                f"[LLM_INPUT] Doc {doc_index} content_len={len(content)}, "
                f"preview={content[:200]!r}"
            )

            result = self.extractor(document_text=content, document_title=title)

            # Log raw LLM response for debugging
            logger.info(f"[LLM_RAW] Doc {doc_index} result type: {type(result)}")

            numbers_str = getattr(result, "structured_numbers", "")
            logger.info(
                f"[LLM_RAW] Doc {doc_index} structured_numbers: {numbers_str!r}"
            )

            # Strip markdown code block wrapper (14B coder models)
            numbers_str = strip_markdown_wrapper(numbers_str)

            if isinstance(numbers_str, str):
                numbers = json.loads(numbers_str)
                logger.info(
                    f"[LLM_PARSED] Doc {doc_index} Parsed {len(numbers)} numbers from JSON string"
                )
            elif isinstance(numbers_str, list):
                numbers = numbers_str
                logger.info(
                    f"[LLM_PARSED] Doc {doc_index} Got {len(numbers)} numbers as list"
                )
            else:
                logger.warning(
                    f"[LLM_FAIL] Doc {doc_index} Unexpected type: {type(numbers_str)}, returning empty"
                )
                return []

            for num in numbers:
                num["source_doc"] = doc_index
                num["source_title"] = title
                num["url"] = url

            return numbers

        except json.JSONDecodeError as e:
            logger.warning(f"[LLM_FAIL] Doc {doc_index} JSON decode error: {e}")
            logger.warning(
                f"[LLM_FAIL] Doc {doc_index} Raw string was: {numbers_str!r}"
            )
            return []
        except (TypeError, AttributeError) as e:
            logger.warning(f"[LLM_FAIL] Doc {doc_index} Error: {e}")
            logger.warning(f"[LLM_FAIL] Doc {doc_index} Result was: {result!r}")
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
