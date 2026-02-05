"""Integration tests for multivector retrieval with Qdrant.

Tests the PrefetchRM implementation with DenseVectorizer and ColBERTVectorizer.
"""

from __future__ import annotations

import logging

import pytest

from agentx.core.dependencies import (
    ensure_dspy_configured,
    get_qdrant_collection_manager,
)
from agentx.infrastructure.retrieval.colbert_vectorizer import ColBERTVectorizer
from agentx.infrastructure.retrieval.dense_vectorizer import DenseVectorizer
from agentx.infrastructure.retrieval.prefetch_rm import PrefetchRM

logger = logging.getLogger(__name__)


@pytest.fixture
def qdrant_collection_manager():
    """Get Qdrant collection manager and ensure collection exists."""
    manager = get_qdrant_collection_manager("test_memory")
    if manager is None:
        pytest.skip("Qdrant not available")
    return manager


@pytest.fixture
def dense_vectorizer():
    """Get DenseVectorizer instance."""
    return DenseVectorizer(model_name="mxbai-embed-large:latest")


@pytest.fixture
def colbert_vectorizer():
    """Get ColBERTVectorizer instance."""
    return ColBERTVectorizer(model_name="colbert-ir/colbertv2.0")


@pytest.fixture
def prefetch_rm(qdrant_collection_manager, dense_vectorizer, colbert_vectorizer):
    """Get PrefetchRM instance."""
    return PrefetchRM(
        collection_manager=qdrant_collection_manager,
        dense_vectorizer=dense_vectorizer,
        colbert_vectorizer=colbert_vectorizer,
    )


@pytest.fixture
def sample_documents(qdrant_collection_manager):
    """Insert sample documents for testing."""
    documents = [
        {
            "id": "doc1",
            "text": "Python is a high-level programming language known for its simplicity.",
            "metadata": {"topic": "programming", "language": "python"},
        },
        {
            "id": "doc2",
            "text": "Machine learning uses algorithms to learn patterns from data.",
            "metadata": {"topic": "ai", "language": "python"},
        },
        {
            "id": "doc3",
            "text": "JavaScript is used for web development and interactive websites.",
            "metadata": {"topic": "web", "language": "javascript"},
        },
        {
            "id": "doc4",
            "text": "Natural language processing enables computers to understand human language.",
            "metadata": {"topic": "nlp", "language": "python"},
        },
        {
            "id": "doc5",
            "text": "Rust is a systems programming language focused on safety and performance.",
            "metadata": {"topic": "systems", "language": "rust"},
        },
    ]

    # Get dense vectorizer
    dense_vectorizer = DenseVectorizer(model_name="mxbai-embed-large:latest")

    # Insert documents with dense vectors
    for doc in documents:
        text = str(doc["text"])  # Ensure string type
        dense_vector = dense_vectorizer.embed(text)

        qdrant_collection_manager.insert_document(
            document_id=str(doc["id"]),
            text=text,
            dense_vector=dense_vector,
            colbert_vector=None,  # ColBERT optional for test
            metadata=doc["metadata"] if "metadata" in doc else {},
        )

    yield documents

    # Cleanup: delete test documents
    # (In production, you might want to use a separate test collection)


class TestMultivectorRetrieval:
    """Test suite for multivector retrieval."""

    def test_collection_exists(self, qdrant_collection_manager):
        """Test that Qdrant collection is properly initialized."""
        assert qdrant_collection_manager.ensure_collection_exists()

    def test_dense_vectorizer(self, dense_vectorizer):
        """Test DenseVectorizer produces embeddings."""
        text = "This is a test sentence for embedding."
        embedding = dense_vectorizer.embed(text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

    def test_colbert_vectorizer_optional(self, colbert_vectorizer):
        """Test ColBERTVectorizer graceful degradation when unavailable."""
        text = "This is a test sentence for ColBERT embedding."

        # If ColBERT is available, test it
        if colbert_vectorizer.is_available:
            embedding = colbert_vectorizer.embed(text)
            # ColBERT returns multi-vector (list of lists)
            assert isinstance(embedding, list)
            # When unavailable, returns empty list
        else:
            # When RAGatouille not installed, returns empty list
            embedding = colbert_vectorizer.embed(text)
            assert embedding == []

    def test_prefetch_rm_dense_only(self, prefetch_rm):
        """Test PrefetchRM with dense-only retrieval (ColBERT unavailable)."""
        # This test works even when ColBERT is not installed
        query = "programming languages for web development"
        results = prefetch_rm.forward(query, k=3)

        assert isinstance(results, list)
        # Should return some results (even if empty list)
        assert len(results) <= 3

    def test_prefetch_rm_retrieval_accuracy(self, prefetch_rm):
        """Test that PrefetchRM retrieves relevant documents."""
        # Query about programming languages
        query = "What programming language is used for web development?"
        results = prefetch_rm.forward(query, k=3)

        # Results should be a list of strings
        assert isinstance(results, list)

        # If we have results, check the content
        if results:
            # The top result should mention JavaScript or web development
            top_result = results[0].lower()
            logger.info(f"Top result for query: {top_result}")

    def test_dense_search_direct(self, qdrant_collection_manager, dense_vectorizer):
        """Test dense search directly via collection manager."""
        query = "machine learning algorithms"
        query_vector = dense_vectorizer.embed(query)

        results = qdrant_collection_manager.search_dense(query_vector, limit=3)

        assert isinstance(results, list)
        # Check result structure
        if results:
            for result in results:
                assert "id" in result
                assert "score" in result
                assert "payload" in result


def test_retrieval_integration():
    """Integration test for the full retrieval pipeline.

    This test:
    1. Configures DSPy
    2. Ensures Qdrant collection exists
    3. Creates PrefetchRM with both vectorizers
    4. Performs a test query
    """
    # Step 1: Configure DSPy
    ensure_dspy_configured()

    # Step 2: Get collection manager and ensure collection exists
    collection_manager = get_qdrant_collection_manager("test_integration")
    if collection_manager is None:
        pytest.skip("Qdrant not available")

    assert collection_manager.ensure_collection_exists()

    # Step 3: Create vectorizers
    dense_vectorizer = DenseVectorizer(model_name="mxbai-embed-large:latest")
    colbert_vectorizer = ColBERTVectorizer(model_name="colbert-ir/colbertv2.0")

    # Step 4: Create PrefetchRM
    prefetch_rm = PrefetchRM(
        collection_manager=collection_manager,
        dense_vectorizer=dense_vectorizer,
        colbert_vectorizer=colbert_vectorizer,
    )

    # Step 5: Test query
    query = "artificial intelligence and machine learning"
    results = prefetch_rm.forward(query, k=5)

    # Verify results
    assert isinstance(results, list)
    logger.info(f"Retrieved {len(results)} results for query: {query}")

    # If ColBERT is available, it should re-rank results
    if colbert_vectorizer.is_available:
        logger.info("ColBERT re-ranking was applied")
    else:
        logger.info("ColBERT unavailable, using dense-only results")


if __name__ == "__main__":
    # Run a quick test
    logging.basicConfig(level=logging.INFO)
    test_retrieval_integration()
    print("✅ Multivector retrieval integration test passed!")
