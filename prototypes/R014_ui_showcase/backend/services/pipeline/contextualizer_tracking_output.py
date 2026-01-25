# =============================================================================
# AGENTX Contextualizer - Output Data Tracking
# =============================================================================
# Tracks final assembly and output of contextualizer
# =============================================================================

import logging

logger = logging.getLogger(__name__)


def track_build_return(
    beautiful_data: dict,
    contextualized_data_final: list,
    top_facts: list,
    research_data: dict,
) -> None:
    """Track final return build.

    Shows what data is being passed to next stage.
    """
    logger.info("      [BUILD RETURN] Assembling output:")

    logger.info(f"        - beautiful_data: {list(beautiful_data.keys())}")

    for key, val in beautiful_data.items():
        if isinstance(val, list):
            logger.info(f"          - {key}: {len(val)} items")

    logger.info(f"        - contextualized_data: {len(contextualized_data_final)} docs")
    logger.info(f"        - top_facts: {len(top_facts)} items")
    logger.info("        - Preserving from research_data:")

    preserved_fields = [
        "structured_report",
        "structured_data",
        "query",
        "citations",
        "url_list",
        "documents",
    ]

    for field in preserved_fields:
        value = research_data.get(field)
        if isinstance(value, list):
            logger.info(f"          - {field}: {len(value)} items")
        elif isinstance(value, dict):
            logger.info(f"          - {field}: {len(value)} keys")
        elif isinstance(value, str):
            logger.info(f"          - {field}: '{value[:30]}...' (len={len(value)})")
        else:
            logger.info(f"          - {field}: {type(value).__name__}")
