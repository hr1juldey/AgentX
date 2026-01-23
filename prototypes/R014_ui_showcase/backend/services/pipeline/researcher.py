# =============================================================================
# AGENTX RESEARCHER Agent
# =============================================================================
# Phase 2: Beautiful Data + SearXNG
# =============================================================================

import logging
from typing import Optional

import dspy

from services.pipeline.researcher_filter import (
    filter_and_log_results,
    sort_and_deduplicate,
)
from services.pipeline.researcher_process import process_research_data
from services.pipeline.researcher_result import build_researcher_result
from services.pipeline.researcher_search import (
    execute_multi_term_search,
    execute_single_search,
)
from services.tools.researcher import (
    BeautifierModule,
    CitationBuilderModule,
    DataStructurerModule,
    SearXNGSearchModule,
)

logger = logging.getLogger(__name__)


class ResearcherAgent(dspy.Module):
    """RESEARCHER Agent: Fetches data, makes it beautiful, organizes, structures, cites.

    Uses SearXNG to fetch live web data and processes it for presentation.
    """

    def __init__(self, searxng_url: str = "http://192.168.1.4:8080"):
        super().__init__()
        # Tools for research
        self.searcher = SearXNGSearchModule(searxng_url=searxng_url)
        self.beautifier = BeautifierModule()
        self.structurer = DataStructurerModule()
        self.citer = CitationBuilderModule()

    def forward(
        self,
        analysis: dict,
        previous_data: Optional[dict] = None,
    ) -> dict:
        """Execute RESEARCHER agent pipeline.

        Args:
            analysis: Analysis result from ANALYST agent
            previous_data: Previous research data (for follow-up searches)

        Returns:
            Researched and processed data
        """
        # Use search_terms if available, otherwise fall back to goal/query
        search_terms = analysis.get("search_terms", [])
        if search_terms:
            # Multiple search terms - search with each and combine results
            all_results, query_for_display = execute_multi_term_search(
                self.searcher, search_terms
            )
            sorted_results = sort_and_deduplicate(all_results)
            raw_data_for_beautify = filter_and_log_results(
                sorted_results,
                source_description=f"results from {len(search_terms)} terms",
            )
        else:
            # Fall back to single query
            query = analysis.get("query", analysis.get("goal", ""))
            raw_results, query_for_display = execute_single_search(self.searcher, query)
            sorted_results = sort_and_deduplicate(raw_results)
            raw_data_for_beautify = filter_and_log_results(
                sorted_results, source_description="results from single query"
            )

        # Process data through beautifier, structurer, citation builder
        beautiful_data, structured_data, citations = process_research_data(
            beautifier=self.beautifier,
            structurer=self.structurer,
            citer=self.citer,
            raw_data=raw_data_for_beautify,
            query_display=query_for_display,
        )

        return build_researcher_result(
            raw_data=raw_data_for_beautify,
            beautiful_data=beautiful_data,
            structured_data=structured_data,
            citations=citations,
            analysis=analysis,
        )
