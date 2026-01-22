# =============================================================================
# AGENTX Contextualizer - Filter Module
# =============================================================================
# Filters noise and low-quality results
# =============================================================================

import dspy

from services.tools.common.type_utils import _to_bool, _to_float
from services.tools.contextualizer.signatures import (
    CheckRelevanceSignature,
    ShouldIncludeSignature,
)


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
