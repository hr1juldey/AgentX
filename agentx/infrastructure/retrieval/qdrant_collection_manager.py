"""Qdrant collection management for named vector configurations.

Manages Qdrant collections with support for multiple named vectors
(dense embeddings and ColBERT multi-vectors).

Supports both per-agent private collections and shared knowledge collections.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from qdrant_client.models import (
    Distance,
    HnswConfigDiff,
    MultiVectorConfig,
    MultiVectorComparator,
    PointStruct,
    VectorParams,
)

if TYPE_CHECKING:
    from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class QdrantCollectionManager:
    """Manager for Qdrant collections with named vectors.

    Handles collection creation, validation, and configuration for
    storing both dense and ColBERT embeddings in the same collection.

    Supports per-agent collections and shared knowledge collections.
    """

    # Vector name constants (same across all collections)
    DENSE_VECTOR_NAME = "dense"
    COLBERT_VECTOR_NAME = "colbert"

    # Vector dimensions
    DENSE_DIM = 1024  # mxbai-embed-large dimension
    COLBERT_DIM = 128  # colbertv2.0 dimension

    # Distance metric (Cosine for semantic search)
    DISTANCE = Distance.COSINE

    def __init__(self, qdrant_client: QdrantClient, collection_name: str) -> None:
        """Initialize the collection manager.

        Args:
            qdrant_client: Qdrant client instance
            collection_name: Name of the collection (e.g., "research_agent_memory",
                           "chatbot_agent_memory", or "agentx_knowledge" for shared)
        """
        self._client = qdrant_client
        self.collection_name = collection_name

        logger.info(
            f"QdrantCollectionManager initialized for collection: {collection_name}"
        )

    def ensure_collection_exists(self) -> bool:
        """Ensure the collection exists with proper configuration.

        Creates the collection if it doesn't exist, or validates
        configuration if it does.

        Returns:
            True if collection is ready, False otherwise
        """
        try:
            # Check if collection exists
            collections = self._client.get_collections()
            collection_names = {col.name for col in collections.collections}

            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return self._validate_collection()
            else:
                return self._create_collection()

        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            return False

    def _create_collection(self) -> bool:
        """Create a new collection with named vectors.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Configure named vectors as dict (medical bot pattern)
            vectors_config = {
                # Dense vector for fast retrieval (indexed)
                self.DENSE_VECTOR_NAME: VectorParams(
                    size=self.DENSE_DIM,
                    distance=self.DISTANCE,
                    # HNSW indexing by default for fast search
                ),
                # ColBERT multivector for reranking (NOT indexed)
                self.COLBERT_VECTOR_NAME: VectorParams(
                    size=self.COLBERT_DIM,
                    distance=self.DISTANCE,
                    multivector_config=MultiVectorConfig(
                        comparator=MultiVectorComparator.MAX_SIM
                    ),
                    hnsw_config=HnswConfigDiff(m=0),  # NO indexing for reranker!
                ),
            }

            # Create collection
            self._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=vectors_config,
            )

            logger.info(
                f"Created collection '{self.collection_name}' with "
                f"named vectors: {self.DENSE_VECTOR_NAME} ({self.DENSE_DIM}D), "
                f"{self.COLBERT_VECTOR_NAME} ({self.COLBERT_DIM}D multivector)"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False

    def _validate_collection(self) -> bool:
        """Validate existing collection configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            collection_info = self._client.get_collection(self.collection_name)

            # Check for named vectors (dict type in new API)
            vectors_config = collection_info.config.params.vectors
            if not isinstance(vectors_config, dict):
                logger.warning(
                    f"Collection '{self.collection_name}' exists but "
                    "doesn't have named vectors configured"
                )
                return False

            vector_names = list(vectors_config.keys())

            # Verify required vectors exist
            has_dense = self.DENSE_VECTOR_NAME in vector_names
            has_colbert = self.COLBERT_VECTOR_NAME in vector_names

            if not has_dense or not has_colbert:
                logger.warning(
                    f"Collection '{self.collection_name}' missing required vectors. "
                    f"Has: {vector_names}, Required: "
                    f"[{self.DENSE_VECTOR_NAME}, {self.COLBERT_VECTOR_NAME}]"
                )
                return False

            logger.info(f"Collection '{self.collection_name}' validated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to validate collection: {e}")
            return False

    def insert_document(
        self,
        document_id: str,
        text: str,
        dense_vector: list[float],
        colbert_vector: list[list[float]] | None = None,
        metadata: dict | None = None,
    ) -> bool:
        """Insert a document with both dense and ColBERT vectors.

        Args:
            document_id: Unique document identifier
            text: Document text content
            dense_vector: Dense embedding vector
            colbert_vector: ColBERT multi-vector (optional)
            metadata: Additional metadata payload

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare vectors dict
            vectors: dict[str, object] = {
                self.DENSE_VECTOR_NAME: dense_vector,
            }

            # Add ColBERT multivector if provided
            if colbert_vector:
                vectors[self.COLBERT_VECTOR_NAME] = colbert_vector

            # Prepare payload
            payload = {
                "text": text,
                "metadata": metadata or {},
            }

            # Create point
            point = PointStruct(
                id=document_id,
                vector=vectors,
                payload=payload,
            )

            # Insert point
            self._client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )

            logger.debug(
                f"Inserted document '{document_id}' in '{self.collection_name}' "
                f"with {len(vectors)} vectors"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to insert document: {e}")
            return False

    def search_with_prefetch(
        self,
        dense_query: list[float],
        colbert_query: list[list[float]],
        limit: int = 5,
        prefetch_limit: int = 100,
    ) -> list[dict]:
        """Search using prefetch pattern: dense retrieve, ColBERT rerank.

        This is the recommended pattern from Qdrant medical bot example.

        Args:
            dense_query: Dense query embedding for initial retrieval
            colbert_query: ColBERT query multivector for reranking
            limit: Number of final results to return
            prefetch_limit: Number of candidates to retrieve with dense

        Returns:
            List of search results with payload
        """
        try:
            from qdrant_client.models import Prefetch

            # Prefetch pattern: retrieve with dense, rerank with ColBERT
            results = self._client.query_points(
                collection_name=self.collection_name,
                prefetch=[
                    Prefetch(
                        query=dense_query,
                        using=self.DENSE_VECTOR_NAME,
                        limit=prefetch_limit,
                    )
                ],
                query=colbert_query,
                using=self.COLBERT_VECTOR_NAME,
                limit=limit,
                with_payload=True,
            )

            # Extract results with safe payload access
            output = []
            for hit in results.points:
                payload = (
                    hit.payload
                    if hasattr(hit, "payload") and hit.payload is not None
                    else {}
                )
                output.append(
                    {
                        "id": hit.id,
                        "score": hit.score,
                        "payload": payload,
                        "text": payload.get("text", "")
                        if isinstance(payload, dict)
                        else "",
                    }
                )
            return output

        except Exception as e:
            logger.error(f"Prefetch search failed: {e}")
            return []

    def search_dense(self, query_vector: list[float], limit: int = 100) -> list[dict]:
        """Search using dense vector only.

        Args:
            query_vector: Dense query embedding
            limit: Number of results to return

        Returns:
            List of search results with payload
        """
        try:
            results = self._client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                using=self.DENSE_VECTOR_NAME,
                limit=limit,
                with_payload=True,
            )

            # Extract results with safe payload access
            output = []
            for hit in results.points:
                payload = (
                    hit.payload
                    if hasattr(hit, "payload") and hit.payload is not None
                    else {}
                )
                output.append(
                    {
                        "id": hit.id,
                        "score": hit.score,
                        "payload": payload,
                        "text": payload.get("text", "")
                        if isinstance(payload, dict)
                        else "",
                    }
                )
            return output

        except Exception as e:
            logger.error(f"Dense search failed: {e}")
            return []

    def delete_collection(self) -> bool:
        """Delete the collection (use with caution).

        Returns:
            True if successful, False otherwise
        """
        try:
            self._client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False
