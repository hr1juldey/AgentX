# =============================================================================
# AGENTX Master Agent - Pipeline Data Tracking
# =============================================================================
# Strategic loggers for detecting data loss/leak across pipeline stages
# =============================================================================

import logging

logger = logging.getLogger(__name__)


def _log_list_counts(label: str, data: dict, keys: list[str]) -> None:
    """Log counts for specified list keys in data dict.

    Args:
        label: Section label for grouping
        data: Data dictionary to extract counts from
        keys: List of keys to count
    """
    logger.info(f"      {label}:")
    for key in keys:
        items = data.get(key, [])
        if isinstance(items, list):
            logger.info(f"        - {key}: {len(items)} items")
        else:
            logger.info(f"        - {key}: {type(items).__name__}")


def track_contextualizer_output(result: dict) -> None:
    """Track data leaving contextualizer phase.

    Logs counts of all arrays and presence of key fields.
    """
    beautiful = result.get("beautiful_data", {})

    logger.info("    → [CONTEXTUALIZER OUTPUT] Data tracking:")

    # Log beautiful_data arrays
    _log_list_counts(
        "beautiful_data", beautiful, ["key_facts", "trends", "comparisons"]
    )

    # Log other key fields
    contextualized = result.get("contextualized_data", [])
    citations = result.get("citations", [])
    structured = result.get("structured_data", {})
    query = result.get("query", "")
    search_terms = result.get("search_terms", [])

    logger.info("      core_data:")
    logger.info(f"        - contextualized_data: {len(contextualized)} docs")
    logger.info(f"        - citations: {len(citations)} items")
    logger.info(f"        - structured_data: {len(structured)} keys")
    logger.info(f"        - query: {bool(query)} (len={len(query)})")
    logger.info(f"        - search_terms: {len(search_terms)} items")

    if search_terms:
        logger.info(f"        - search_terms sample: {search_terms[:2]}")


def track_research_merge(first: dict, additional: dict, merged: dict) -> None:
    """Track research merge operation with before/after comparison.

    Detects data loss by comparing merged counts against inputs.
    """
    logger.info("    → [MERGE] Research data merge:")

    # Count documents before merge
    first_docs = len(first.get("contextualized_data", []))
    add_docs = len(additional.get("contextualized_data", []))
    merged_docs = len(merged.get("contextualized_data", []))

    # Count citations before merge
    first_cites = len(first.get("citations", []))
    add_cites = len(additional.get("citations", []))
    merged_cites = len(merged.get("citations", []))

    # Log before/after
    logger.info(f"      documents: {first_docs} + {add_docs} → {merged_docs}")
    logger.info(f"      citations: {first_cites} + {add_cites} → {merged_cites}")

    # Detect data loss
    if merged_docs < max(first_docs, add_docs):
        logger.warning(
            f"      ⚠️  DATA LOSS: Documents decreased from max({first_docs}, {add_docs}) to {merged_docs}"
        )
    if merged_cites < max(first_cites, add_cites):
        logger.warning(
            f"      ⚠️  DATA LOSS: Citations decreased from max({first_cites}, {add_cites}) to {merged_cites}"
        )


def track_presenter_input(researched_data: dict) -> None:
    """Track data entering presenter phase (hydrators receive this).

    Logs what data is available to chart/markdown/card hydrators.
    """
    beautiful = researched_data.get("beautiful_data", {})
    structured = researched_data.get("structured_data", {})
    citations = researched_data.get("citations", [])
    query = researched_data.get("query", "")
    urls = researched_data.get("url_list", [])

    logger.info("    → [PRESENTER INPUT] Data for hydrators:")

    # Log beautiful_data (used by all hydrators)
    _log_list_counts(
        "beautiful_data", beautiful, ["key_facts", "trends", "comparisons"]
    )

    # Log other fields
    logger.info("      other_fields:")
    logger.info(f"        - structured_data keys: {list(structured.keys())[:5]}")
    logger.info(f"        - citations: {len(citations)} items")
    logger.info(f"        - query: '{query[:50]}' (len={len(query)})")
    logger.info(f"        - url_list: {len(urls)} URLs")
