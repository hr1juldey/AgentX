# =============================================================================
# AGENTX Researcher - Multi-Hop Web Reader
# =============================================================================
# "Z-read on steroids" - Multi-hop web reading with n² report generation
# =============================================================================
# Formula: Total reports = n² where n = number of hops
# Example: 3 hops → 3² = 9 total reports (NOT cumulative)
# =============================================================================

import logging

from services.tools.researcher.web_fetcher import (
    fetch_page,
    truncate_content,
)
from services.tools.researcher.content_filter import ContentFilterModule
from services.tools.researcher.report_generator import ReportGeneratorModule

logger = logging.getLogger(__name__)


class MultiHopReader:
    """Multi-hop web reader that generates n² micro reports.

    Two modes:
    1. Basic mode: Single URL → extract relevant content + generate report
    2. Multi-hop mode: Multiple URLs → recursive link following → n² reports

    The n² formula: Total reports = n² where n = number of hops
    - 3 hops → 9 reports total (distributed across pages, not 1+9+27)
    - Reports per hop decreases as we go deeper (early pages get more reports)

    Context management:
    - Content truncated to 2000 chars before filtering
    - Only filtered content (relevant parts) sent to LLM
    - Max 3 links extracted per page to avoid explosion
    """

    MIN_HOPS = 3
    MAX_HOPS = 5
    DEFAULT_HOPS = 3

    # Content limits to avoid context rotting
    MAX_CONTENT_LENGTH = 2000
    MAX_REPORTS_PER_PAGE = 3

    def __init__(self):
        self.filter = ContentFilterModule()
        self.reporter = ReportGeneratorModule()

    async def basic_read(self, url: str, goal: str) -> dict:
        """Basic mode: Read single URL and extract relevant content.

        Args:
            url: URL to read
            goal: Research goal

        Returns:
            Dict with url, title, relevant_content, report
        """
        logger.info(f"[BASIC READ] Fetching: {url}")

        page = await fetch_page(url)
        if not page:
            return {"url": url, "error": "Failed to fetch"}

        # Extract relevant content
        relevant = self.filter.filter_content(
            page_content=page["markdown_content"],
            goal=goal,
        )

        # Generate micro report
        report_dict = {}
        if relevant:
            report_dict = self.reporter.generate_report(
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

    async def multihop_read(
        self,
        urls: list[str],
        goal: str,
        max_hops: int = DEFAULT_HOPS,
    ) -> dict:
        """Multi-hop mode: Recursive web reading with n² report generation.

        Args:
            urls: Initial list of URLs to read
            goal: Research goal
            max_hops: Number of hops (3-5, default 3)

        Returns:
            Dict with all_reports (list), total_count, citations, trajectory
        """
        # Validate hops
        max_hops = max(self.MIN_HOPS, min(max_hops, self.MAX_HOPS))

        target_reports = max_hops**2  # n² formula
        logger.info(
            f"[MULTIHOP] Starting: {max_hops} hops → {target_reports} reports target"
        )

        all_reports: list[dict] = []
        all_citations: list[dict] = []
        trajectory: list[dict] = []

        # Track URLs we've already seen (avoid cycles)
        seen_urls = set(urls)

        # Queue of (url, hop_level) tuples
        from collections import deque

        queue = deque([(url, 1) for url in urls])

        # Calculate approximate reports needed per hop level
        # Early pages get more reports, later pages get fewer
        reports_per_level = target_reports // max_hops

        hop_counts = {i: 0 for i in range(1, max_hops + 1)}

        while queue and len(all_reports) < target_reports:
            url, hop_level = queue.popleft()

            if hop_level > max_hops:
                continue

            logger.info(f"[HOP {hop_level}/{max_hops}] Fetching: {url}")

            # Check if we've generated enough reports for this level
            if hop_counts[hop_level] >= reports_per_level:
                logger.info(
                    f"[HOP {hop_level}] Reached {reports_per_level} reports, skipping"
                )
                continue

            # Fetch page
            page = await fetch_page(url)
            if not page:
                trajectory.append(
                    {
                        "hop": hop_level,
                        "url": url,
                        "status": "failed",
                    }
                )
                continue

            # Filter relevant content
            relevant = self.filter.filter_content(
                page_content=truncate_content(
                    page["markdown_content"],
                    self.MAX_CONTENT_LENGTH,
                ),
                goal=goal,
            )

            trajectory.append(
                {
                    "hop": hop_level,
                    "url": url,
                    "title": page.get("title", "")[:50],
                    "relevant_chars": len(relevant),
                    "links_found": len(page.get("links", [])),
                    "status": "success",
                }
            )

            # Generate report if we found relevant content
            if relevant and hop_counts[hop_level] < reports_per_level:
                report_dict = self.reporter.generate_report(
                    content=relevant,
                    goal=goal,
                    source_url=url,
                )

                if report_dict["report"]:
                    all_reports.append(
                        {
                            **report_dict,
                            "hop_level": hop_level,
                            "source_title": page.get("title", ""),
                        }
                    )
                    hop_counts[hop_level] += 1

                    all_citations.append(
                        {
                            "url": url,
                            "title": page.get("title", ""),
                            "report_snippet": report_dict["report"][:100],
                        }
                    )

            # Extract relevant links for next hop (limit to avoid explosion)
            if hop_level < max_hops:
                relevant_links = self.filter.extract_links(
                    links=page.get("links", []),
                    goal=goal,
                )

                for link in relevant_links:
                    link_url = link["url"]
                    if link_url not in seen_urls:
                        seen_urls.add(link_url)
                        queue.append((link_url, hop_level + 1))

            logger.info(
                f"[HOP {hop_level}] Reports so far: {len(all_reports)}/{target_reports}"
            )

        logger.info(
            f"[MULTIHOP] Complete: {len(all_reports)} reports from {max_hops} hops"
        )

        return {
            "all_reports": all_reports,
            "total_count": len(all_reports),
            "citations": all_citations,
            "trajectory": trajectory,
            "hop_distribution": hop_counts,
            "target_reports": target_reports,
        }
