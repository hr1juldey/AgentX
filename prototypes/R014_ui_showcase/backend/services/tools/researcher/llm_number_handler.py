# =============================================================================
# AGENTX Number Extractor - LLM Number Handler
# =============================================================================
# Handles LLM-based number extraction from documents
# =============================================================================

"""LLM-based number extraction handler.

This module encapsulates the logic for extracting structured numbers
from document text using DSPy LLM chains. It handles:
- LLM invocation via DSPy ChainOfThought
- Markdown wrapper stripping (14B coder models)
- JSON parsing and validation
- Source metadata injection
- Error handling and logging

Interface: extract_numbers_from_document()
"""

import json
import logging

from services.tools.researcher.number_extractor_utils import strip_markdown_wrapper

logger = logging.getLogger(__name__)


def extract_numbers_from_document(
    extractor,
    content: str,
    title: str,
    url: str,
    doc_index: int,
) -> list:
    """Extract numbers from document using LLM.

    Args:
        extractor: DSPy ChainOfThought(ExtractDocumentNumbers) instance
        content: Document content text (up to 5000 chars)
        title: Document title for LLM context
        url: Document URL for citation metadata
        doc_index: Document index for logging

    Returns:
        List of extracted number dicts with source metadata added.
        Returns empty list on any error (signals regex fallback needed).

    Interface contract:
        - Returns empty list → caller should use regex fallback
        - Returns non-empty list → extraction succeeded
        - All errors are logged before returning
    """
    result = None
    numbers_str = ""

    try:
        # Log input for debugging
        has_full = len(content) > 2000  # Heuristic: full content > 2000 chars
        logger.info(
            f"[LLM_INPUT] Doc {doc_index} content_len={len(content)}, "
            f"has_full_content={has_full}, "
            f"preview={content[:200]!r}"
        )

        # Call LLM
        result = extractor(document_text=content, document_title=title)

        # Log raw response
        logger.info(f"[LLM_RAW] Doc {doc_index} result type: {type(result)}")
        numbers_str = getattr(result, "structured_numbers", "")
        logger.info(f"[LLM_RAW] Doc {doc_index} structured_numbers: {numbers_str!r}")

        # Strip markdown wrapper (14B coder models wrap JSON in ``` blocks)
        numbers_str = strip_markdown_wrapper(numbers_str)

        # Parse JSON
        if isinstance(numbers_str, str):
            numbers = json.loads(numbers_str)
            logger.info(
                f"[LLM_PARSED] Doc {doc_index} Parsed {len(numbers)} numbers from JSON"
            )
        elif isinstance(numbers_str, list):
            numbers = numbers_str
            logger.info(
                f"[LLM_PARSED] Doc {doc_index} Got {len(numbers)} numbers as list"
            )
        else:
            logger.warning(
                f"[LLM_FAIL] Doc {doc_index} Unexpected type: {type(numbers_str)}, "
                f"returning empty"
            )
            return []

        # Validate and filter out entries with non-numeric values
        validated_numbers = []
        for num in numbers:
            # LLM may return either 'value' or 'numeric_value' key
            value = num.get("value") or num.get("numeric_value")
            # Skip if value is not numeric (int, float, or numeric string)
            try:
                float(value)
                # Value is numeric, accept it
                # Ensure 'value' key exists for downstream consistency
                if "value" not in num and "numeric_value" in num:
                    num["value"] = num["numeric_value"]
                num["source_doc"] = doc_index
                num["source_title"] = title
                num["url"] = url
                validated_numbers.append(num)
            except (ValueError, TypeError):
                # Value is non-numeric (e.g., "1970s_level", "N/A", None)
                logger.warning(
                    f"[LLM_VALIDATE] Doc {doc_index} Skipped non-numeric value: {value!r}"
                )

        if len(validated_numbers) < len(numbers):
            logger.info(
                f"[LLM_VALIDATE] Doc {doc_index} Filtered {len(validated_numbers)}/{len(numbers)} entries (removed non-numeric values)"
            )

        return validated_numbers

    except json.JSONDecodeError as e:
        logger.warning(f"[LLM_FAIL] Doc {doc_index} JSON decode error: {e}")
        logger.warning(f"[LLM_FAIL] Doc {doc_index} Raw string was: {numbers_str!r}")
        return []

    except (TypeError, AttributeError) as e:
        logger.warning(f"[LLM_FAIL] Doc {doc_index} Error: {e}")
        logger.warning(f"[LLM_FAIL] Doc {doc_index} Result was: {result!r}")
        return []
