# =============================================================================
# AGENTX Regex Fallback for Number Extraction
# =============================================================================
# Extracts structured numbers using regex patterns (LLM fallback)
# =============================================================================

import logging
import re

logger = logging.getLogger(__name__)


# Regex patterns for number extraction
PATTERNS = [
    r"(\w+(?:\s+\w+)*)\s*[:]\s*([\d.]+)\s*([%$])?(?:\s*(\d{4}))?",  # "US: 3.7% 2023"
    r"([\d.]+)\s*([%$])(?:\s*(\d{4}))?\s*(\w+(?:\s+\w+)*)",  # "3.7% 2023 US inflation"
    r"(\w+(?:\s+\w+)*)\s*(\d+\.?\d*)\s*(?:percent|%|billion|million|thousand)",  # "GDP 5.2 percent"
]


def extract_numbers_with_regex(
    content: str, title: str, url: str, doc_index: int
) -> list:
    """Extract numbers using regex as fallback.

    Args:
        content: Document content text
        title: Document title
        url: Document URL
        doc_index: Document index in raw_data

    Returns:
        List of extracted number dicts
    """
    numbers = []

    for pattern in PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            groups = match.groups()

            # Parse based on pattern
            if groups[0] and groups[0][0].isdigit():  # Number comes first
                value_str = groups[0]
                unit = groups[1] if len(groups) > 1 else ""
                label = groups[3] if len(groups) > 3 else ""
                year = groups[2] if len(groups) > 2 and groups[2] else None
            else:  # Label comes first
                label = groups[0]
                value_str = groups[1]
                unit = groups[2] if len(groups) > 2 else ""
                year = groups[3] if len(groups) > 3 else None

            try:
                value = float(value_str.replace(",", ""))
            except ValueError:
                continue

            numbers.append(
                {
                    "label": label.strip(),
                    "value": value,
                    "unit": unit.strip(),
                    "context": "extracted",
                    "year": year,
                    "source_doc": doc_index,
                    "source_title": title,
                    "url": url,
                }
            )

    return numbers
