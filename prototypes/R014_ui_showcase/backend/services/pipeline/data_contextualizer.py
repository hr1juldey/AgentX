# =============================================================================
# AGENTX DATA CONTEXTUALIZER Agent
# =============================================================================
# Phase 3: Rerank, Filter, Contextualize
# =============================================================================

import dspy

from services.tools.contextualizer import (
    ContextualizerModule,
    FilterModule,
    RerankerModule,
)


class DataContextualizerAgent(dspy.Module):
    """DATA CONTEXTUALIZER Agent: Reranks, filters, and contextualizes data.

    Takes research output and adds query context, removes noise,
    reranks by relevance for the specific query.
    """

    def __init__(self):
        super().__init__()
        # Tools for contextualization
        self.reranker = RerankerModule()
        self.filter = FilterModule()
        self.contextualizer = ContextualizerModule()

    def forward(
        self,
        research_data: dict,
        original_query: str = "",
    ) -> dict:
        """Execute DATA CONTEXTUALIZER agent pipeline.

        Args:
            research_data: Research output from RESEARCHER agent
            original_query: Original user query for context

        Returns:
            Contextualized and reranked data
        """
        query = research_data.get("query", original_query)
        raw_data = research_data.get("raw_data", [])
        beautiful_data = research_data.get("beautiful_data", {})

        # Step 1: Rerank by relevance
        ranked_result_raw = self.reranker(query=query, results=raw_data)
        ranked_result = ranked_result_raw if hasattr(ranked_result_raw, "get") else {}

        # Step 2: Filter out noise
        ranked_data_for_filter = (
            ranked_result.get("ranked_data", raw_data)
            if hasattr(ranked_result, "get")
            else raw_data
        )
        filtered_result_raw = self.filter(
            query=query,
            results=ranked_data_for_filter,
        )
        filtered_result = (
            filtered_result_raw if hasattr(filtered_result_raw, "get") else {}
        )

        # Step 3: Add query context
        filtered_data_for_context = (
            filtered_result.get("filtered_data", [])
            if hasattr(filtered_result, "get")
            else []
        )
        contextualized_result_raw = self.contextualizer(
            query=query,
            filtered_data=filtered_data_for_context,
            original_query=original_query,
        )
        contextualized_result = (
            contextualized_result_raw
            if hasattr(contextualized_result_raw, "get")
            else {}
        )

        contextualized_data_final = (
            contextualized_result.get("contextualized_data", [])
            if hasattr(contextualized_result, "get")
            else []
        )

        return {
            "ranked_data": ranked_result.get("ranked_data", [])
            if hasattr(ranked_result, "get")
            else [],
            "relevance_scores": ranked_result.get("scores", [])
            if hasattr(ranked_result, "get")
            else [],
            "filtered_data": filtered_result.get("filtered_data", [])
            if hasattr(filtered_result, "get")
            else [],
            "removed_count": filtered_result.get("removed_count", 0)
            if hasattr(filtered_result, "get")
            else 0,
            "contextualized_data": contextualized_data_final,
            "query_relevance": contextualized_result.get("query_relevance", "Medium")
            if hasattr(contextualized_result, "get")
            else "Medium",
            "beautiful_data": {
                **beautiful_data,
                "key_facts": self._extract_top_facts(contextualized_data_final),
            },
        }

    def _extract_top_facts(self, contextualized_data: list) -> list:
        """Extract top facts from contextualized data."""
        if not contextualized_data:
            return []

        facts = []
        for item in contextualized_data[:5]:
            if isinstance(item, dict):
                if "title" in item:
                    facts.append(item["title"])
                elif "text" in item:
                    facts.append(
                        item["text"][:100] + "..."
                        if len(item.get("text", "")) > 100
                        else item.get("text", "")
                    )
            else:
                facts.append(str(item)[:100])

        return facts
