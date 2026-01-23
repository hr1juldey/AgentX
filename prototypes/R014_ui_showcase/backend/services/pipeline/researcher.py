# =============================================================================
# AGENTX RESEARCHER Agent
# =============================================================================
# Phase 2: Beautiful Data + SearXNG
# =============================================================================

from typing import Optional

import dspy

from services.pipeline.researcher_helpers import (
    determine_data_type,
    generate_summary_report,
)
from services.tools.researcher import (
    BeautifierModule,
    CitationBuilderModule,
    DataStructurerModule,
    SearXNGSearchModule,
)


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
        domain = analysis.get("domain", "general")
        query_for_log = analysis.get("query", "")

        # Use search_terms if available, otherwise fall back to goal/query
        search_terms = analysis.get("search_terms", [])
        if search_terms:
            # Multiple search terms - search with each and combine results
            all_results = []
            for term in search_terms:
                search_results_raw = self.searcher(query=term, search_type="general")
                search_results = (
                    search_results_raw if hasattr(search_results_raw, "get") else {}
                )
                all_results.extend(search_results.get("raw_data", []))

            # Deduplicate by URL
            seen_urls = set()
            unique_results = []
            for result in all_results:
                url = result.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)

            raw_data_for_beautify = unique_results
            query_for_display = (
                f"{len(search_terms)} terms: {', '.join(search_terms[:3])}"
            )
        else:
            # Fall back to single query
            query = analysis.get("query", analysis.get("goal", ""))
            search_results_raw = self.searcher(query=query, search_type="general")
            search_results = (
                search_results_raw if hasattr(search_results_raw, "get") else {}
            )
            raw_data_for_beautify = (
                search_results.get("raw_data", [])
                if hasattr(search_results, "get")
                else []
            )
            query_for_display = query

        # Beautify raw data
        beautiful_data_raw = self.beautifier(
            raw_data=raw_data_for_beautify,
            query=query_for_display,
        )
        beautiful_data = (
            beautiful_data_raw if hasattr(beautiful_data_raw, "get") else {}
        )

        # Structure the beautiful data
        structured_data_raw = self.structurer(beautiful_data=beautiful_data)
        structured_data = (
            structured_data_raw if hasattr(structured_data_raw, "get") else {}
        )

        # Build citations
        citations_raw = self.citer(raw_data=raw_data_for_beautify)
        citations = citations_raw if hasattr(citations_raw, "get") else []

        return {
            "raw_data": raw_data_for_beautify,
            "beautiful_data": {
                "key_facts": beautiful_data.get("key_facts", [])
                if hasattr(beautiful_data, "get")
                else [],
                "trends": beautiful_data.get("trends", [])
                if hasattr(beautiful_data, "get")
                else [],
                "comparisons": beautiful_data.get("comparisons", [])
                if hasattr(beautiful_data, "get")
                else [],
            },
            "structured_data": structured_data,
            "citations": citations,
            "structured_report": generate_summary_report(
                beautiful_data if isinstance(beautiful_data, dict) else {},
                citations if isinstance(citations, list) else [],
                domain,
            ),
            "data_type": determine_data_type(
                analysis, beautiful_data if isinstance(beautiful_data, dict) else {}
            ),
            "query": query_for_log,
        }
