# =============================================================================
# AGENTX Researcher - Multi-Hop Processor
# =============================================================================
# Processes individual hops in multi-hop web reading
# =============================================================================

import logging
from collections import deque

from services.tools.researcher.web_fetcher import fetch_page, truncate_content


logger = logging.getLogger(__name__)


async def process_hop(
    url: str,
    hop_level: int,
    goal: str,
    max_hops: int,
    reports_per_level: int,
    hop_counts: dict[int, int],
    filter_instance,
    reporter_instance,
) -> tuple[dict, dict | None, dict | None, dict | None]:
    """Process a single hop in the multi-hop reading pipeline.

    Args:
        url: URL to fetch
        hop_level: Current hop level (1-based)
        goal: Research goal
        max_hops: Maximum number of hops
        reports_per_level: Target reports per hop level
        hop_counts: Running count of reports per level
        filter_instance: ContentFilterModule instance
        reporter_instance: ReportGeneratorModule instance

    Returns:
        Tuple of (trajectory_entry, report_dict, citation_dict, link_dicts)
    """
    trajectory_entry = {
        "hop": hop_level,
        "url": url,
        "status": "pending",
    }

    # Check if we've generated enough reports for this level
    if hop_counts[hop_level] >= reports_per_level:
        trajectory_entry["status"] = "skipped"
        logger.info(f"[HOP {hop_level}] Reached {reports_per_level} reports, skipping")
        return trajectory_entry, None, None, None

    logger.info(f"[HOP {hop_level}/{max_hops}] Fetching: {url}")

    # Fetch page
    page = await fetch_page(url)
    if not page:
        trajectory_entry["status"] = "failed"
        return trajectory_entry, None, None, None

    # Filter relevant content
    relevant = filter_instance.filter_content(
        page_content=truncate_content(page["markdown_content"], 2000),
        goal=goal,
    )

    trajectory_entry.update(
        {
            "title": page.get("title", "")[:50],
            "relevant_chars": len(relevant),
            "links_found": len(page.get("links", [])),
            "status": "success",
        }
    )

    # Generate report if we found relevant content
    report_dict = None
    citation_dict = None

    if relevant and hop_counts[hop_level] < reports_per_level:
        report_dict = reporter_instance.generate_report(
            content=relevant,
            goal=goal,
            source_url=url,
        )

        if report_dict["report"]:
            citation_dict = {
                "url": url,
                "title": page.get("title", ""),
                "report_snippet": report_dict["report"][:100],
            }

    # Extract relevant links for next hop (limit to 3 to avoid explosion)
    link_dicts = []
    if hop_level < max_hops:
        link_dicts = filter_instance.extract_links(
            links=page.get("links", []),
            goal=goal,
        )

    return trajectory_entry, report_dict, citation_dict, link_dicts


def initialize_multihop_queue(urls: list[str]) -> deque:
    """Initialize the BFS queue for multi-hop reading.

    Args:
        urls: Initial list of URLs

    Returns:
        Queue of (url, hop_level) tuples
    """
    return deque([(url, 1) for url in urls])
