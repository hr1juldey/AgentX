# =============================================================================
# AGENTX Researcher - Multi-Hop Web Reader
# =============================================================================
# "Z-read on steroids" - Multi-hop web reading with n² report generation
# =============================================================================
# Formula: Total reports = n² where n = number of hops
# Example: 3 hops → 3² = 9 total reports (NOT cumulative)
# =============================================================================

import logging

from services.tools.researcher.content_filter import ContentFilterModule
from services.tools.researcher.multihop_basic import basic_read
from services.tools.researcher.multihop_processor import (
    initialize_multihop_queue,
    process_hop,
)
from services.tools.researcher.report_generator import ReportGeneratorModule

logger = logging.getLogger(__name__)


class MultiHopReader:
    """Multi-hop web reader generating n² micro reports.

    Two modes:
    1. Basic: Single URL → extract relevant content + generate report
    2. Multi-hop: Multiple URLs → recursive link following → n² reports

    n² formula: Total reports = n² where n = hops (e.g., 3 hops → 9 reports total)
    Reports distributed across pages, not cumulative. Context limits: 2000 chars,
    only filtered content sent to LLM, max 3 links per page.
    """

    # Hop configuration
    MIN_HOPS = 3
    MAX_HOPS = 5
    DEFAULT_HOPS = 3
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
        return await basic_read(url, goal, self.filter, self.reporter)

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
        max_hops = max(self.MIN_HOPS, min(max_hops, self.MAX_HOPS))

        target_reports = max_hops**2  # n² formula
        logger.info(
            f"[MULTIHOP] Starting: {max_hops} hops → {target_reports} reports target"
        )

        all_reports: list[dict] = []
        all_citations: list[dict] = []
        trajectory: list[dict] = []

        reports_per_level = target_reports // max_hops
        hop_counts = {i: 0 for i in range(1, max_hops + 1)}
        queue = initialize_multihop_queue(urls)
        seen_urls = set(urls)

        while queue and len(all_reports) < target_reports:
            url, hop_level = queue.popleft()

            if hop_level > max_hops:
                continue

            traj_entry, report_dict, citation_dict, link_dicts = await process_hop(
                url=url,
                hop_level=hop_level,
                goal=goal,
                max_hops=max_hops,
                reports_per_level=reports_per_level,
                hop_counts=hop_counts,
                filter_instance=self.filter,
                reporter_instance=self.reporter,
            )

            trajectory.append(traj_entry)

            if report_dict and report_dict["report"]:
                all_reports.append(
                    {
                        **report_dict,
                        "hop_level": hop_level,
                        "source_title": traj_entry.get("title", ""),
                    }
                )
                hop_counts[hop_level] += 1

                if citation_dict:
                    all_citations.append(citation_dict)

            if link_dicts:
                for link in link_dicts:
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
