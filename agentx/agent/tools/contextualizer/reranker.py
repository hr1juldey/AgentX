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
    """

    def __init__(self) -> None:
        """Initialize the relevance scorer."""
        super().__init__()
        self.reorder = dspy.Predict(ReorderContext)
        self.assess = dspy.Predict(AssessContextQuality)

    def forward(self, query: str, context_chunks: list[dict]) -> dict:
        """Score and reorder context chunks.

        Args:
            query: User's original question
            context_chunks: List of context dicts with text and source

        Returns:
            dict with 'reordered_context' (list) and 'scores' (list)
        """
        if not context_chunks:
            return {
                "reordered_context": [],
                "scores": [],
            }

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
            should_keep = safe_extract(result, "should_keep", True)

            # Calculate combined score
            combined_score = (quality * 0.3) + (relevance * 0.7)

            if should_keep:
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

        # Extract reordered context and scores
        reordered_context = [item["chunk"] for item in scored_chunks]
        scores = [
            {
                "quality": item["quality"],
                "relevance": item["relevance"],
                "combined": item["combined_score"],
            }
            for item in scored_chunks
        ]

        return {
            "reordered_context": reordered_context,
            "scores": scores,
        }
