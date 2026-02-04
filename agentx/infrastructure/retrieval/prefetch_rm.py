"""Prefetch RM wrapper - dense (fast) → ColBERT (accurate) pattern."""

from dspy.primitives.retriever import Retriever  # type: ignore[import]


class PrefetchRM(Retriever):
    """Retriever with prefetch: dense for speed, ColBERT for accuracy."""

    def __init__(self) -> None:
        """Initialize the prefetch retriever.

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("PrefetchRM not yet implemented")

    def forward(self, query: str, k: int = 5) -> list[str]:
        """Retrieve relevant documents with prefetch fallback.

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of document contents

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("PrefetchRM.forward() not yet implemented")
