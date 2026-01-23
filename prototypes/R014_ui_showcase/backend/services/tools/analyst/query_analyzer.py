# =============================================================================
# AGENTX Analyst - Query Analyzer Modules
# =============================================================================
# Analyzes query context and extracts insights
# =============================================================================

import dspy
from typing import List


class ContextAnalyzerModule(dspy.Module):
    """Analyzes the context and domain of the user query."""

    def __init__(self):
        super().__init__()
        self.detect_type = dspy.Predict("query -> query_type")
        self.extract_domain = dspy.Predict("query -> domain")
        self.identify_urgency = dspy.Predict("query -> urgency")

    def forward(self, query: str) -> dict:
        """Analyze query context."""
        type_result = self.detect_type(query=query)
        domain_result = self.extract_domain(query=query)
        urgency_result = self.identify_urgency(query=query)

        return {
            "query_type": type_result.query_type,  # type: ignore[attr-defined]
            "domain": domain_result.domain,  # type: ignore[attr-defined]
            "urgency": urgency_result.urgency,  # type: ignore[attr-defined]
        }


class InsightExtractorModule(dspy.Module):
    """Extracts insights using chunking + iterative refinement.

    Uses decision tree:
    1. If text < 500 chars → direct extraction
    2. If text > 500 chars → chunk + iterate 3 times
    3. Deduplicate results
    """

    MAX_CHUNK_SIZE = 500
    OVERLAP = 100
    ITERATIONS = 3

    def __init__(self):
        super().__init__()
        from services.tools.analyst.signatures import (
            ExtractInitialInsights,
            RefineInsights,
        )

        self.initial_extractor = dspy.Predict(ExtractInitialInsights)
        self.refiner = dspy.Predict(RefineInsights)

    def forward(self, query: str) -> dict:
        # Decision tree: small query?
        if len(query) <= self.MAX_CHUNK_SIZE:
            return self._extract_single(query)

        # Large query: chunk + iterate
        return self._extract_iterative(query)

    def _extract_single(self, query: str) -> dict:
        """Fast path for small queries."""
        result = self.initial_extractor(text_chunk=query)
        insights = self._parse_insights(result.insights)
        return {"insights": insights, "key_questions": []}

    def _extract_iterative(self, query: str) -> dict:
        """Chunk + iterate for large text."""
        from services.core.chunking import chunk_text, deduplicate_items

        chunks = chunk_text(query, self.MAX_CHUNK_SIZE, self.OVERLAP)
        all_insights = []
        existing = ""

        for i, chunk in enumerate(chunks[: self.ITERATIONS]):
            if i == 0:
                result = self.initial_extractor(text_chunk=chunk)
                all_insights.extend(self._parse_insights(result.insights))
            else:
                result = self.refiner(text_chunk=chunk, existing_insights=existing)
                all_insights.extend(self._parse_insights(result.new_insights))

            existing = ", ".join([ins[:30] for ins in all_insights])

        unique_insights = deduplicate_items(all_insights)
        return {"insights": unique_insights, "key_questions": []}

    def _parse_insights(self, insights_str: str) -> List[str]:
        """Parse insight string into list."""
        if not insights_str:
            return []
        return [
            line.strip().lstrip("-").strip()
            for line in insights_str.split("\n")
            if line.strip() and line.strip().startswith("-")
        ]
