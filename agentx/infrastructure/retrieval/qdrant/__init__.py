"""Qdrant infrastructure subpackage.

Contains modular components for Qdrant collection management,
split per file size requirements.
"""

from agentx.infrastructure.retrieval.qdrant.collection import (
    create_collection,
    validate_collection,
)
from agentx.infrastructure.retrieval.qdrant.constants import (
    COLBERT_DIM,
    COLBERT_VECTOR_NAME,
    DENSE_DIM,
    DENSE_DISTANCE,
    DENSE_VECTOR_NAME,
)
from agentx.infrastructure.retrieval.qdrant.search import (
    search_dense,
    search_with_prefetch,
)
from agentx.infrastructure.retrieval.qdrant.writer import (
    insert_document,
    insert_documents_batch,
)

__all__ = [
    # Constants
    "DENSE_VECTOR_NAME",
    "COLBERT_VECTOR_NAME",
    "DENSE_DIM",
    "COLBERT_DIM",
    "DENSE_DISTANCE",
    # Collection config
    "create_collection",
    "validate_collection",
    # Document writer
    "insert_document",
    "insert_documents_batch",
    # Search
    "search_dense",
    "search_with_prefetch",
]
