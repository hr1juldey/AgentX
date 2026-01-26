# =============================================================================
# AGENTX Researcher - Multi-Hop Basic Read
# =============================================================================
# Single URL reading mode for multi-hop reader
# =============================================================================

import logging

from services.tools.researcher.content_filter import ContentFilterModule
from services.tools.researcher.report_generator import ReportGeneratorModule
from services.tools.researcher.web_fetcher import fetch_page

logger = logging.getLogger(__name__)


async def basic_read(
    url: str,
    goal: str,
    filter_instance: ContentFilterModule,
    reporter_instance: ReportGeneratorModule,
) -> dict:
    """Basic mode: Read single URL and extract relevant content.

    Args:
        url: URL to read
        goal: Research goal
        filter_instance: ContentFilterModule instance
        reporter_instance: ReportGeneratorModule instance

    Returns:
        Dict with url, title, relevant_content, report
    """
    logger.info(f"[BASIC READ] Fetching: {url}")

    page = await fetch_page(url)
    if not page:
        return {"url": url, "error": "Failed to fetch"}

    # Extract relevant content
    relevant = filter_instance.filter_content(
        page_content=page["markdown_content"],
        goal=goal,
    )

    # Generate micro report
    report_dict = {}
    if relevant:
        report_dict = reporter_instance.generate_report(
            content=relevant,
            goal=goal,
            source_url=url,
        )

    logger.info(f"[BASIC READ] Extracted {len(relevant)} chars, generated report")

    return {
        "url": url,
        "title": page.get("title", ""),
        "relevant_content": relevant,
        "report": report_dict.get("report", ""),
        "source_url": url,
        "word_count": report_dict.get("word_count", 0),
    }
