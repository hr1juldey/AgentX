# =============================================================================
# AGENTX RESEARCHER Agent
# =============================================================================
# Phase 2: Beautiful Data + SearXNG
# =============================================================================

from typing import Optional

import dspy

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
        query = analysis.get("query", analysis.get("goal", ""))
        domain = analysis.get("domain", "general")

        # Search SearXNG
        search_results_raw = self.searcher(query=query, search_type="general")
        search_results = (
            search_results_raw if hasattr(search_results_raw, "get") else {}
        )

        # Beautify raw data
        raw_data_for_beautify = (
            search_results.get("raw_data", []) if hasattr(search_results, "get") else []
        )
        beautiful_data_raw = self.beautifier(
            raw_data=raw_data_for_beautify,
            query=query,
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
            "structured_report": self._generate_summary_report(
                beautiful_data if isinstance(beautiful_data, dict) else {},
                citations if isinstance(citations, list) else [],
                domain,
            ),
            "data_type": self._determine_data_type(
                analysis, beautiful_data if isinstance(beautiful_data, dict) else {}
            ),
            "query": query,
        }

    def _generate_summary_report(
        self,
        beautiful_data: dict,
        citations: list,
        domain: str,
    ) -> str:
        """Generate a summary report from research."""
        parts = []

        key_facts = (
            beautiful_data.get("key_facts", [])
            if hasattr(beautiful_data, "get")
            else []
        )
        trends = (
            beautiful_data.get("trends", []) if hasattr(beautiful_data, "get") else []
        )

        if key_facts:
            parts.append("Key findings: " + ", ".join(key_facts[:3]))

        if trends:
            parts.append("Trends: " + ", ".join(trends[:3]))

        return " | ".join(parts) if parts else f"Research completed for {domain}"

    def _determine_data_type(self, analysis: dict, beautiful_data: dict) -> str:
        """Determine the type of data for widget selection."""
        query = analysis.get("query", "").lower()
        domain = analysis.get("domain", "").lower()

        if "price" in query or "stock" in query or "finance" in domain:
            return "numerical_time_series"
        if "image" in query or "photo" in query:
            return "visual_image"
        if "comparison" in query:
            return "comparative"

        return "general"
