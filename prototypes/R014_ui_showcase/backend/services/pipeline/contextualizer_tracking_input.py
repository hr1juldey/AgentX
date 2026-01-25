# =============================================================================
# AGENTX Contextualizer - Input Data Tracking
# =============================================================================
# Tracks data entering contextualizer
# =============================================================================

import logging

logger = logging.getLogger(__name__)


def track_input_data(research_data: dict) -> None:
    """Track data entering contextualizer.

    Shows what fields are present in the input.
    """
    logger.info("    → [CONTEXTUALIZER INPUT] Received data:")

    raw_data = research_data.get("raw_data", [])
    beautiful = research_data.get("beautiful_data", {})
    structured = research_data.get("structured_data", {})
    query = research_data.get("query", "")
    search_terms = research_data.get("search_terms", [])

    logger.info(f"      - raw_data: {len(raw_data)} items")
    logger.info(f"      - beautiful_data keys: {list(beautiful.keys())}")

    for key, val in beautiful.items():
        if isinstance(val, list):
            logger.info(f"        - {key}: {len(val)} items")

    logger.info(f"      - structured_data keys: {list(structured.keys())[:5]}")
    logger.info(f"      - query: '{query[:50]}...' (len={len(query)})")
    logger.info(f"      - search_terms: {len(search_terms)} items")
