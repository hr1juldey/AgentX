"""ColBERT Qdrant collection management.

Handles Qdrant collection lifecycle for multivector storage.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    MultiVectorConfig,
    MultiVectorComparator,
    VectorParams,
)


class ColBERTQdrantManager:
    """Manages Qdrant collections for ColBERT embeddings."""

    VECTOR_SIZE = 128

    def __init__(self, qdrant_url: str = "http://localhost:6333") -> None:
        """Initialize Qdrant manager.

        Args:
            qdrant_url: Qdrant server URL
        """
        self.client = QdrantClient(url=qdrant_url)

    def ensure_collection(self, collection_name: str) -> None:
        """Create Qdrant collection with multivector config.

        Args:
            collection_name: Name of the collection
        """
        collections = [c.name for c in self.client.get_collections().collections]
        if collection_name not in collections:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                    multivector_config=MultiVectorConfig(
                        comparator=MultiVectorComparator.MAX_SIM
                    ),
                ),
            )
