# =============================================================================
# AGENTX Contextualizer - Reranker Module
# =============================================================================
# Reranks search results by relevance
# =============================================================================

import dspy

from services.tools.common.type_utils import _to_float
from services.tools.contextualizer.signatures import ScoreRelevanceSignature


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
