"""Qdrant RM with prefetch (dense → ColBERT)."""


class PrefetchQdrantRM:
    """Retriever with prefetch: dense (fast) → ColBERT (accurate)."""

    def __init__(self) -> None:
        """Initialize the prefetch retriever.

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("PrefetchQdrantRM not yet implemented")

    def retrieve(self, query: str, k: int = 5) -> list[str]:
        """Retrieve relevant documents.

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of document contents

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("PrefetchQdrantRM.retrieve() not yet implemented")
