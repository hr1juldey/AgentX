# =============================================================================
# AGENTX Contextualizer Tools
# =============================================================================
# DSPy modules for the DATA CONTEXTUALIZER agent (Rerank, Filter, Contextualize)
# =============================================================================

import dspy

from services.tools.common import _to_bool, _to_float


# =============================================================================
# DSPy Signatures with proper type annotations
# =============================================================================


class ScoreRelevanceSignature(dspy.Signature):
    """Score a single result's relevance to the query."""

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to score")
    relevance_score: float = dspy.OutputField(desc="Relevance score from 0.0 to 1.0")


class CheckRelevanceSignature(dspy.Signature):
    """Check if a result is relevant to the query."""

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to check")
    is_relevant: bool = dspy.OutputField(desc="Whether the result is relevant")
    relevance_score: float = dspy.OutputField(desc="Relevance score from 0.0 to 1.0")


class ShouldIncludeSignature(dspy.Signature):
    """Determine if a result should be included in filtered results."""

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to evaluate")
    should_include: bool = dspy.OutputField(desc="Whether to include this result")
    reason: str = dspy.OutputField(desc="Reason for inclusion/exclusion")


# =============================================================================
# DSPy Modules
# =============================================================================


class RerankerModule(dspy.Module):
    """Reranks search results by relevance.

    Has 2 signatures:
    - ScoreRelevance: Score each result's relevance to query (returns float)
    - RankByQuality: Rank results by quality score
    """

    def __init__(self):
        super().__init__()
        # Use class-based signature with float type annotation
        self.score_relevance = dspy.Predict(ScoreRelevanceSignature)
        self.rank_by_quality = dspy.Predict("query, results -> ranked_results")

    def forward(self, query: str, results: list) -> dict:
        """Rerank results by relevance."""
        # Score each result
        scored_results = []
        for result in results:
            score_result = self.score_relevance(query=query, result=str(result))
            if hasattr(score_result, "relevance_score"):
                result_copy = result.copy() if isinstance(result, dict) else result
                # Safely convert to float
                score = _to_float(score_result.relevance_score)  # type: ignore[attr-defined]
                scored_results.append({"data": result_copy, "score": score})

        # Sort by score
        scored_results.sort(key=lambda x: x["score"], reverse=True)

        # Rank by quality
        ranked_result = self.rank_by_quality(query=query, results=str(scored_results))

        return {
            "ranked_data": [r["data"] for r in scored_results],
            "scores": [r["score"] for r in scored_results],
            "ranked_results": ranked_result.ranked_results
            if hasattr(ranked_result, "ranked_results")
            else scored_results,
        }


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
                include_result.should_include,  # type: ignore[attr-defined]  # pyrefly: ignore[missing-attribute]
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
