# =============================================================================
# AGENTX Contextualizer - Filter Module
# =============================================================================
# Filters noise and low-quality results
# =============================================================================

import asyncio

import dspy

from config.settings import settings
from services.tools.common.type_utils import _to_bool, _to_float
from services.tools.contextualizer.async_executor import execute_parallel
from services.tools.contextualizer.signatures import (
    CheckRelevanceSignature,
    ShouldIncludeSignature,
)

# Semaphore to limit concurrent LLM calls (prevents overwhelming Ollama)
_concurrency_semaphore = asyncio.Semaphore(settings.max_concurrent)


class FilterModule(dspy.Module):
    """Filters noise and low-quality results.

    Has 2 signatures:
    - ShouldInclude: Determine if result should be included (returns bool)
    - CheckRelevance: Check if result is relevant to query (returns float)
    """

    def __init__(self):
        super().__init__()
        # Use class-based signatures with proper types
        self.should_include = dspy.Predict(ShouldIncludeSignature)
        self.check_relevance = dspy.Predict(CheckRelevanceSignature)

    def forward(self, query: str, results: list) -> dict:
        """Filter results to remove noise."""
        filtered_results = []

        for result in results:
            include_result = self.should_include(query=query, result=str(result))
            relevance_result = self.check_relevance(query=query, result=str(result))

            # Safely convert bool
            should_include = _to_bool(
                include_result.should_include,  # type: ignore[attr-defined]
                default=True,
            )

            if should_include:
                result_copy = result.copy() if isinstance(result, dict) else result
                if isinstance(result_copy, dict):
                    if hasattr(relevance_result, "relevance_score"):
                        # Safely convert to float
                        result_copy["relevance_score"] = _to_float(
                            relevance_result.relevance_score  # type: ignore[attr-defined]
                        )
                filtered_results.append(result_copy)

        return {
            "filtered_data": filtered_results,
            "removed_count": len(results) - len(filtered_results),
        }

    async def aforward(self, query: str, results: list) -> dict:
        """Async filter results to remove noise with parallel processing."""

        async def filter_result(result, sem):
            async with sem:
                include_result = await self.should_include.acall(
                    query=query, result=str(result)
                )
                relevance_result = await self.check_relevance.acall(
                    query=query, result=str(result)
                )

                should_include = _to_bool(
                    include_result.should_include,  # type: ignore[attr-defined]
                    default=True,
                )

                if should_include:
                    result_copy = result.copy() if isinstance(result, dict) else result
                    if isinstance(result_copy, dict):
                        if hasattr(relevance_result, "relevance_score"):
                            result_copy["relevance_score"] = _to_float(
                                relevance_result.relevance_score  # type: ignore[attr-defined]
                            )
                    return result_copy
                return None

        filtered_results = await execute_parallel(
            results, filter_result, _concurrency_semaphore
        )

        return {
            "filtered_data": filtered_results,
            "removed_count": len(results) - len(filtered_results),
        }
