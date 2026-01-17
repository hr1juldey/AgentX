"""Smart search service with Qdrant and FastEmbed."""

import logging
from typing import List, Optional

import fastembed
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from config.settings import settings
from models.schemas import DocumentCreate, SearchRequest, SearchResult

logger = logging.getLogger(__name__)


class SearchService:
    """Service for vector search using Qdrant and FastEmbed."""

    def __init__(self):
        """Initialize the search service."""
        self.client: Optional[QdrantClient] = None
        self.embedding_model: Optional[fastembed.TextEmbedding] = None
        self._initialize_qdrant()
        self._initialize_embeddings()

    def _initialize_qdrant(self):
        """Initialize Qdrant client and collection."""
        try:
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )

            # Create collection if it doesn't exist
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if settings.qdrant_collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=settings.qdrant_collection_name,
                    vectors_config=VectorParams(
                        size=384,  # BGE-small dimension
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created collection: {settings.qdrant_collection_name}")
            else:
                logger.info(f"Using existing collection: {settings.qdrant_collection_name}")

        except Exception as e:
            logger.warning(f"Qdrant not available: {e}. Using in-memory mode.")
            self.client = None

    def _initialize_embeddings(self):
        """Initialize embedding model."""
        try:
            self.embedding_model = fastembed.TextEmbedding(model_name=settings.embedding_model)
            logger.info(f"Loaded embedding model: {settings.embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text."""
        if not self.embedding_model:
            return None

        try:
            embedding = list(self.embedding_model.embed([text]))[0]
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    async def add_document(self, document: DocumentCreate) -> Optional[str]:
        """Add a document to the search index."""
        if not self.client or not self.embedding_model:
            logger.warning("Qdrant or embedding model not available")
            return None

        try:
            import hashlib

            doc_id = hashlib.md5(document.content.encode()).hexdigest()
            embedding = self._generate_embedding(document.content)

            if not embedding:
                return None

            point = PointStruct(
                id=doc_id,
                vector=embedding,
                payload={"content": document.content, "metadata": document.metadata or {}},
            )

            self.client.upsert(collection_name=settings.qdrant_collection_name, points=[point])

            logger.info(f"Added document: {doc_id}")
            return doc_id

        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return None

    async def search(self, request: SearchRequest) -> List[SearchResult]:
        """Search for similar documents."""
        if not self.client or not self.embedding_model:
            return []

        try:
            query_embedding = self._generate_embedding(request.query)
            if not query_embedding:
                return []

            top_k = request.top_k or settings.top_k_results
            threshold = request.score_threshold or settings.score_threshold

            results = self.client.search(
                collection_name=settings.qdrant_collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=threshold,
            )

            search_results = []
            for result in results:
                search_results.append(
                    SearchResult(
                        id=str(result.id),
                        content=result.payload.get("content", ""),
                        score=result.score,
                        metadata=result.payload.get("metadata"),
                    )
                )

            return search_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def get_collection_info(self) -> dict:
        """Get collection information."""
        if not self.client:
            return {"connected": False, "collection_exists": False, "document_count": 0}

        try:
            collection_info = self.client.get_collection(
                collection_name=settings.qdrant_collection_name
            )
            return {
                "connected": True,
                "collection_exists": True,
                "document_count": collection_info.points_count,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"connected": True, "collection_exists": False, "document_count": 0}


# Global service instance
search_service = SearchService()
