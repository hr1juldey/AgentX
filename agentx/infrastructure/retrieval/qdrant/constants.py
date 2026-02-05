"""Qdrant vector configuration constants."""

from qdrant_client.models import Distance


# Vector name constants (same across all collections)
DENSE_VECTOR_NAME = "dense"
COLBERT_VECTOR_NAME = "colbert"

# Vector dimensions
DENSE_DIM = 1024  # mxbai-embed-large dimension
COLBERT_DIM = 128  # colbertv2.0 dimension

# Distance metric (Cosine for semantic search)
# Note: For dense vector only. ColBERT uses MAX_SIM comparator instead.
DENSE_DISTANCE = Distance.COSINE
