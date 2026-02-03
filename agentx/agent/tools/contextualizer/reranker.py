"""Relevance Scorer Module for Contextualizer agent.

Ported from R014: services/tools/contextualizer/reranker.py

Reorders context chunks by relevance to query using semantic similarity.
"""

import dspy

from agentx.agent.dspy_signatures.contextualizer.reranking import (
    ReorderContext,
    AssessContextQuality,
)
from agentx.agent.tools.common.dspy_helpers import safe_extract
from agentx.agent.tools.common.type_utils import _to_float


class RelevanceScorerModule(dspy.Module):
    """Scores and reorders context chunks by relevance.

    Evaluates each context chunk on:
    - Relevance to query
    - Information quality
    - Source credibility

    Returns reordered context from most to least relevant.
    Filters by quality threshold (Fraud #5 fix).
    """

    def __init__(self, quality_threshold: float = 0.6, min_results: int = 3) -> None:
        """Initialize the relevance scorer.

        Args:
            quality_threshold: Minimum combined score to keep a chunk
            min_results: Always return at least this many results
        """
        super().__init__()
        self.reorder = dspy.Predict(ReorderContext)
        self.assess = dspy.Predict(AssessContextQuality)
        self.quality_threshold = quality_threshold
        self.min_results = min_results

    def forward(self, query: str, context_chunks: list[dict]) -> dict:
        """Score and reorder context chunks with quality filtering.

        Args:
            query: User's original question
            context_chunks: List of context dicts with text and source

        Returns:
            dict with 'filtered_results', 'original_count', 'filtered_count'
        """
        if not context_chunks:
            return {
                "filtered_results": [],
                "original_count": 0,
                "filtered_count": 0,
            }

        original_count = len(context_chunks)

        # Score each chunk individually
        scored_chunks = []
        for chunk in context_chunks:
            chunk_text = chunk.get("text", "")
            if not chunk_text:
                continue

            # Assess quality and relevance
            result = self.assess(context_chunk=chunk_text, query=query)

            quality = _to_float(safe_extract(result, "quality_score", 0.5), default=0.5)
            relevance = _to_float(
                safe_extract(result, "relevance_score", 0.5), default=0.5
            )

            # Calculate combined score
            combined_score = (quality * 0.3) + (relevance * 0.7)

            scored_chunks.append(
                {
                    "chunk": chunk,
                    "quality": quality,
                    "relevance": relevance,
                    "combined_score": combined_score,
                }
            )

        # Sort by combined score (descending)
        scored_chunks.sort(key=lambda x: x["combined_score"], reverse=True)

        # Filter by quality threshold (Fraud #5 fix: actual filtering)
        filtered_chunks = []
        for i, item in enumerate(scored_chunks):
            # Always include at least min_results, then filter by threshold
            if i < self.min_results or item["combined_score"] >= self.quality_threshold:
                filtered_chunks.append(item)

        filtered_count = len(filtered_chunks)

        return {
            "filtered_results": [
                {
                    "chunk": item["chunk"],
                    "quality": item["quality"],
                    "relevance": item["relevance"],
                    "combined_score": item["combined_score"],
                }
                for item in filtered_chunks
            ],
            "original_count": original_count,
            "filtered_count": filtered_count,
        }
