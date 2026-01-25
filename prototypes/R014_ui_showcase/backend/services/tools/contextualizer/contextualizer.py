# =============================================================================
# AGENTX Contextualizer - Contextualizer Module
# =============================================================================
# Adds query context to search results
# =============================================================================

import asyncio

import dspy

from config.settings import settings
from services.tools.contextualizer.async_executor import execute_parallel

# Semaphore to limit concurrent LLM calls (prevents overwhelming Ollama)
_concurrency_semaphore = asyncio.Semaphore(settings.max_concurrent)


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

    async def aforward(
        self, query: str, filtered_data: list, original_query: str = ""
    ) -> dict:
        """Async contextualize filtered data with parallel processing."""
        query_str = original_query or query

        async def contextualize_result(result, sem):
            async with sem:
                context_result = await self.add_context.acall(
                    query=query_str, result=str(result)
                )

                result_copy = (
                    result.copy() if isinstance(result, dict) else {"data": result}
                )
                if hasattr(context_result, "contextualized_result"):
                    result_copy["query_context"] = context_result.contextualized_result  # type: ignore[attr-defined]

                return result_copy

        contextualized_data = await execute_parallel(
            filtered_data, contextualize_result, _concurrency_semaphore
        )

        return {
            "contextualized_data": contextualized_data,
            "query": query_str,
            "query_relevance": "High" if contextualized_data else "Low",
        }
