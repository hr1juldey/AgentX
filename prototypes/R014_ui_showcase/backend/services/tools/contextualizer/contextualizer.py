# =============================================================================
# AGENTX Contextualizer - Contextualizer Module
# =============================================================================
# Adds query context to search results
# =============================================================================

import dspy


class ContextualizerModule(dspy.Module):
    """Adds query context to search results.

    Has 2 signatures:
    - AddQueryContext: Enrich results with query context
    - EnrichWithMetadata: Add relevant metadata
    """

    def __init__(self):
        super().__init__()
        self.add_context = dspy.Predict("query, result -> contextualized_result")
        self.enrich_metadata = dspy.Predict("result, metadata -> enriched_result")

    def forward(
        self, query: str, filtered_data: list, original_query: str = ""
    ) -> dict:
        """Contextualize filtered data."""
        contextualized_data = []
        query_str = original_query or query

        for result in filtered_data:
            context_result = self.add_context(query=query_str, result=str(result))

            result_copy = (
                result.copy() if isinstance(result, dict) else {"data": result}
            )
            if hasattr(context_result, "contextualized_result"):
                result_copy["query_context"] = context_result.contextualized_result  # type: ignore[attr-defined]

            contextualized_data.append(result_copy)

        return {
            "contextualized_data": contextualized_data,
            "query": query_str,
            "query_relevance": "High" if contextualized_data else "Low",
        }
