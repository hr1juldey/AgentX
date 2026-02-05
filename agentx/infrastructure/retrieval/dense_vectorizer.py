"""Dense vectorizer for single-vector embeddings.

This module provides backward-compatible re-exports from the vectorizer/ subdirectory.
The actual implementation has been split into focused modules:
- vectorizer.py: Main DenseVectorizer class
- ollama.py: Ollama embedding backend
- sentence_transformers.py: Sentence-transformers embedding backend
"""

from agentx.infrastructure.retrieval.vectorizer.vectorizer import DenseVectorizer

__all__ = ["DenseVectorizer"]
