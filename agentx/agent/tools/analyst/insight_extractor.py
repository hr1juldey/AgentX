"""Insight Extractor Module for Analyst agent.

Ported from R014: services/tools/analyst/query_analyzer.py

Extracts insights using chunking + iterative refinement.
Uses decision tree:
1. If text < 500 chars → direct extraction
2. If text > 500 chars → chunk + iterate 3 times
3. Deduplicate results
"""

import dspy

from agentx.agent.dspy_signatures.analyst import (
    ExtractInitialInsights,
    RefineInsights,
)
from agentx.agent.tools.common.chunking import (
    MAX_CHUNK_SIZE,
    OVERLAP,
    ITERATIONS,
    chunk_text,
    deduplicate_items,
)
from agentx.agent.tools.common.dspy_helpers import safe_extract


class InsightExtractorModule(dspy.Module):
    """Extracts insights using chunking + iterative refinement.

    Uses decision tree:
    1. If text < 500 chars → direct extraction
    2. If text > 500 chars → chunk + iterate 3 times
    3. Deduplicate results
    """

    def __init__(self) -> None:
        """Initialize the insight extractor."""
        super().__init__()
        self.initial_extractor = dspy.Predict(ExtractInitialInsights)
        self.refiner = dspy.Predict(RefineInsights)

    def forward(self, query: str) -> dict:
        """Extract insights from query.

        Args:
            query: User query text to analyze

        Returns:
            dict with 'insights' (list) and 'key_questions' (list)
        """
        # Decision tree: small query?
        if len(query) <= MAX_CHUNK_SIZE:
            return self._extract_single(query)

        # Large query: chunk + iterate
        return self._extract_iterative(query)

    def _extract_single(self, query: str) -> dict:
        """Fast path for small queries.

        Args:
            query: Short query text

        Returns:
            dict with insights and key_questions
        """
        result = self.initial_extractor(text_chunk=query)
        insights = self._parse_insights(safe_extract(result, "insights", ""))
        return {"insights": insights, "key_questions": []}

    def _extract_iterative(self, query: str) -> dict:
        """Chunk + iterate for large text.

        Args:
            query: Long query text to chunk

        Returns:
            dict with insights and key_questions
        """
        chunks = chunk_text(query, MAX_CHUNK_SIZE, OVERLAP)
        all_insights = []
        existing = ""

        for i, chunk in enumerate(chunks[:ITERATIONS]):
            if i == 0:
                result = self.initial_extractor(text_chunk=chunk)
                all_insights.extend(
                    self._parse_insights(safe_extract(result, "insights", ""))
                )
            else:
                result = self.refiner(text_chunk=chunk, existing_insights=existing)
                all_insights.extend(
                    self._parse_insights(safe_extract(result, "new_insights", ""))
                )

            existing = ", ".join([ins[:30] for ins in all_insights])

        unique_insights = deduplicate_items(all_insights, normalize=True, min_length=5)
        return {"insights": unique_insights, "key_questions": []}

    def _parse_insights(self, insights_str: str) -> list:
        """Parse insight string into list.

        Args:
            insights_str: Raw insights string from LLM

        Returns:
            List of insight strings
        """
        if not insights_str:
            return []
        return [
            line.strip().lstrip("-").strip()
            for line in insights_str.split("\n")
            if line.strip()
            and (line.strip().startswith("-") or line.strip().startswith("*"))
        ]
