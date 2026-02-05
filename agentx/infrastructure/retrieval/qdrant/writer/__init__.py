"""Qdrant document insert operations."""

from agentx.infrastructure.retrieval.qdrant.writer.batch import (
    insert_documents_batch,
)
from agentx.infrastructure.retrieval.qdrant.writer.single import insert_document

__all__ = ["insert_document", "insert_documents_batch"]
