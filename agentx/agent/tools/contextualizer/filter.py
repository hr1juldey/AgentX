"""Context Filter Module for Contextualizer agent.

Ported from R014: services/tools/contextualizer/filter.py

Filters out irrelevant, redundant, or low-quality context chunks.

Fraud #19 fix: Returns dspy.Prediction instead of dict.
"""

import dspy

from agentx.agent.dspy_signatures.contextualizer.reranking import FilterContext
from agentx.agent.tools.common.dspy_helpers import safe_extract
from agentx.agent.tools.contextualizer.filtering_logic import (
    format_context,
    parse_filtered_context,
    to_int,
)


class ContextFilterModule(dspy.Module):
    """Filters context chunks to keep only relevant content.

    Removes:
    - Irrelevant chunks (don't address query)
    - Duplicates and near-duplicates
    - Low quality or unreliable sources
    - Redundant information

    Fraud #19 fix: Returns dspy.Prediction instead of dict.
    """

    def __init__(self) -> None:
        """Initialize the context filter."""
        super().__init__()
        self.filter = dspy.Predict(FilterContext)

    def forward(self, query: str, context_chunks: list[dict]) -> dspy.Prediction:
        """Filter context chunks to keep only relevant ones.

        Args:
            query: User's original question
            context_chunks: List of context dicts

        Returns:
            dspy.Prediction with 'filtered_context' (list) and 'stats' (dict)
        """
        if not context_chunks:
            return dspy.Prediction(
                filtered_context=[],
                stats={
                    "total": 0,
                    "kept": 0,
                    "removed": 0,
                    "removal_rate": 0.0,
                },
            )

        # Build context string for DSPy
        context_str = format_context(context_chunks)

        # Run filter
        result = self.filter(query=query, context_chunks=context_str)

        # Parse filtered context
        filtered_str = safe_extract(result, "filtered_context", "")
        filtered_context = parse_filtered_context(filtered_str)

        # Get removal count
        removed_count = to_int(safe_extract(result, "removed_count", 0), default=0)

        # Calculate stats
        total_count = len(context_chunks)
        kept_count = len(filtered_context)

        return dspy.Prediction(
            filtered_context=filtered_context,
            stats={
                "total": total_count,
                "kept": kept_count,
                "removed": removed_count,
                "removal_rate": removed_count / total_count if total_count > 0 else 0.0,
            },
        )
