"""ColBERT embedder for semantic search.

This module provides ColBERTv2 late interaction embedder for Qdrant.
ColBERT provides token-level granularity with MaxSim operation.

This is a facade for backward compatibility. Actual implementation has been
moved to the colbert/ subdirectory.
"""

from agentx.infrastructure.external.colbert import ColBERTEmbedder

__all__ = ["ColBERTEmbedder"]
