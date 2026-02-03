"""RAG context scoring module.

Phase 3 Fix: Extracted from RAGContextGenerator for SRP compliance.
"""


class ContextScorer:
    """Scores context quality based on retrieval results.

    Phase 3 Fix: Extracted from RAGContextGenerator.
    Single Responsibility: Score context quality.
    """

    # Externalized magic numbers (Fraud #5.5)
    HIGH_QUALITY_THRESHOLD: int = 3
    VERY_HIGH_QUALITY_THRESHOLD: int = 7

    def score(self, retrieved: list[str]) -> str:
        """Score context quality based on retrieval count.

        Args:
            retrieved: List of retrieved memory texts

        Returns:
            "high", "medium", or "low" quality score
        """
        count = len(retrieved)

        if count >= self.VERY_HIGH_QUALITY_THRESHOLD:
            return "high"
        elif count >= self.HIGH_QUALITY_THRESHOLD:
            return "medium"
        else:
            return "low"


__all__ = ["ContextScorer"]
