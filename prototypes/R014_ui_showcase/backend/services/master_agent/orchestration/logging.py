# =============================================================================
# AGENTX Master Agent - Pipeline Logging Helpers
# =============================================================================
# Helper functions for detailed pipeline logging
# =============================================================================

import logging

logger = logging.getLogger(__name__)


def log_analysis_result(result: dict) -> None:
    """Log analyst results."""
    domain = result.get("domain", "unknown")
    query_type = result.get("query_type", "unknown")
    intent = result.get("user_intent", "unknown")
    logger.info(f"    → Domain: {domain}, Type: {query_type}, Intent: {intent[:60]}...")


def log_research_result(result: dict) -> None:
    """Log researcher results."""
    docs = result.get("documents", [])
    logger.info(f"    → Found {len(docs)} documents")
    for i, doc in enumerate(docs[:3]):
        title = doc.get("title", "Untitled")[:50]
        logger.info(f"      [{i + 1}] {title}...")
    if len(docs) > 3:
        logger.info(f"      ... and {len(docs) - 3} more")


def log_judgment_result(result: dict) -> None:
    """Log judgment results."""
    quality = result.get("data_quality", "unknown")
    needs_more = result.get("needs_more_research", False)
    completeness = result.get("data_completeness", 0)
    logger.info(
        f"    → Quality: {quality}, Completeness: {completeness:.0%}, More research: {needs_more}"
    )


def log_design_result(result: dict) -> None:
    """Log designer results."""
    color_scheme = result.get("color_scheme", {}).get("primary", "unknown")
    pov = result.get("point_of_view", "neutral")[:30]
    logger.info(f"    → POV: {pov}, Color: {color_scheme}")


def log_widget_selection(result: dict) -> None:
    """Log widget selection results."""
    widgets = result.get("widgets", [])
    logger.info(f"    → Selected {len(widgets)} widgets:")
    for w in widgets[:5]:
        w_type = w.get("type", "unknown")
        w_title = w.get("title", "")[:40]
        logger.info(f"      - {w_type}: {w_title}...")
    if len(widgets) > 5:
        logger.info(f"      ... and {len(widgets) - 5} more")
