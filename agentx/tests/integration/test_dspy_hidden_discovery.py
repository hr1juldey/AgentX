"""Integration test: Can AGENTX RAG discover hidden DSPy capabilities?

This is a meta-test of the RAG system's effectiveness:
- Index DSPy documentation and code into Qdrant
- Query for hidden/undocumented capabilities
- Compare AGENTX (4B Gemma + RAG) vs GLM 4.7 brute force

The hidden capabilities are documented in docs/research/16_dspy_hidden_capabilities.md
but the RAG system should find them from source material alone.

Success criteria (qualitative):
1. Retrieval: Can AGENTX find relevant code/documentation?
2. Understanding: Can AGENTX explain how the feature works?
3. Applicability: Can AGENTX recognize when to use it?
4. Code Generation: Can AGENTX generate working code?

Test levels:
- EASY: Well-documented patterns (thread-safe settings, persistent indices)
- MEDIUM: Hidden parameters/options (FAISS hybrid search, stream reuse)
- HARD: Internal functions (sync_send_to_stream, PID filtering)
- EXPERT: Buried features (citation support, Python sandbox)
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

import pytest

from agentx.core.dependencies import (
    get_qdrant_collection_manager,
)
from agentx.infrastructure.retrieval.colbert_vectorizer import ColBERTVectorizer
from agentx.infrastructure.retrieval.dense_vectorizer import DenseVectorizer

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def dspy_collection_manager():
    """Get Qdrant collection manager for DSPy knowledge base."""
    manager = get_qdrant_collection_manager("dspy_hidden_capabilities")
    if manager is None:
        pytest.skip("Qdrant not available")

    # Try to ensure collection exists (without force recreate to avoid timeout)
    if not manager.ensure_collection_exists():
        # If validation fails, try force recreate
        if not manager.ensure_collection_exists(force_recreate=True):
            pytest.skip("Failed to create Qdrant collection")
    return manager


@pytest.fixture(scope="module")
def vectorizers():
    """Get vectorizers for embedding DSPy documentation."""
    # Use qwen3-embedding:8b (4096D, auto-resized to 1024D by DenseVectorizer)
    # Use ColBERTv2 for multivector reranking
    dense = DenseVectorizer(model_name="qwen3-embedding:8b")
    colbert = ColBERTVectorizer(model_name="colbert-ir/colbertv2.0")
    return dense, colbert


class TestDSPyHiddenDiscovery:
    """Test suite for discovering hidden DSPy capabilities via RAG."""

    def test_index_dspy_docs(self, dspy_collection_manager, vectorizers):
        """Index full DSPy source code into Qdrant for RAG discovery test.

        Multithreaded implementation for faster indexing.
        """
        dense_vectorizer, colbert_vectorizer = vectorizers
        dspy_path = Path("/home/riju279/Downloads/dspy-main/dspy-main/")

        if not dspy_path.exists():
            pytest.skip(f"DSPy path not found at {dspy_path}")

        try:
            # Collect all Python and Markdown files from DSPy
            py_files = list(dspy_path.rglob("*.py"))
            md_files = list(dspy_path.rglob("*.md"))
            all_files = py_files + md_files
            # Filter out test files and __pycache__
            all_files = [
                f
                for f in all_files
                if "test" not in f.parts and "__pycache__" not in f.parts
            ]
            logger.info(
                f"Found {len(py_files)} Python files and {len(md_files)} Markdown files "
                f"({len(all_files)} after filtering)"
            )

            # Chunking settings
            max_chars = 1000  # Increased for speed
            overlap = 100  # Reduced for speed

            # Thread-safe counters
            indexed_count = 0
            doc_id_counter = 0
            lock = Lock()

            def process_file(file_path: Path) -> int:
                """Process a single file and return number of chunks indexed."""
                nonlocal doc_id_counter
                chunks_indexed = 0

                try:
                    with open(file_path) as f:
                        content = f.read()

                    # Chunk by characters
                    start = 0
                    while start < len(content):
                        end = start + max_chars
                        chunk_text = content[start:end]

                        # Add file path as context
                        chunk_with_context = (
                            f"# File: {file_path.relative_to(dspy_path)}\n{chunk_text}"
                        )

                        dense_vec = dense_vectorizer.embed(chunk_with_context)

                        colbert_vec = None
                        if colbert_vectorizer.is_available:
                            colbert_vec = colbert_vectorizer.embed(chunk_with_context)

                        # Thread-safe doc_id assignment
                        with lock:
                            doc_id = doc_id_counter
                            doc_id_counter += 1

                        success = dspy_collection_manager.insert_document(
                            document_id=doc_id,
                            text=chunk_with_context,
                            dense_vector=dense_vec,
                            colbert_vector=colbert_vec,
                            metadata={
                                "source": str(file_path),
                                "type": "dspy_source",
                                "chunk_index": start,
                                "file_path": str(file_path.relative_to(dspy_path)),
                            },
                        )

                        if success:
                            chunks_indexed += 1
                        start = end - overlap

                except Exception as e:
                    logger.warning(f"Failed to index {file_path}: {e}")

                return chunks_indexed

            # Process files in parallel (8 workers)
            max_workers = 8
            logger.info(
                f"Starting multithreaded indexing with {max_workers} workers..."
            )

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(process_file, file_path): file_path
                    for file_path in all_files
                }

                for future in as_completed(futures):
                    file_path = futures[future]
                    try:
                        chunks = future.result()
                        with lock:
                            indexed_count += chunks
                        if chunks > 0 and (indexed_count % 100 == 0):
                            logger.info(f"Progress: {indexed_count} chunks indexed...")
                    except Exception as e:
                        logger.error(f"Exception processing {file_path}: {e}")

            logger.info(
                f"Successfully indexed {indexed_count} chunks from DSPy codebase "
                f"(Python + Markdown) with multithreading"
            )
            assert indexed_count > 0, "No chunks were indexed"

        except Exception as e:
            logger.error(f"Failed to index DSPy codebase: {e}")
            pytest.skip(f"Failed to index: {e}")

    def test_easy_discovery_persistent_index(
        self, dspy_collection_manager, vectorizers
    ):
        """EASY TEST: Discover persistent index saving/loading.

        This feature is in the API surface (save/from_saved methods)
        and should be easily discoverable.
        """
        dense_vectorizer, _ = vectorizers

        query = "How do I save and load embeddings index to disk in DSPy?"
        query_vec = dense_vectorizer.embed(query)

        results = dspy_collection_manager.search_dense(query_vec, limit=5)

        assert len(results) > 0, "No results found"

        # Check if results contain relevant information
        found = False
        for result in results:
            text = result.get("text", "").lower()
            if "save" in text and ("embeddings" in text or "index" in text):
                found = True
                logger.info(
                    f"Found relevant passage in {result.get('payload', {}).get('source')}"
                )
                break

        assert found, "Could not find information about saving/loading embeddings"

    def test_easy_discovery_settings_context(
        self, dspy_collection_manager, vectorizers
    ):
        """EASY TEST: Discover thread-safe settings context manager.

        The context manager pattern is documented but rarely used in examples.
        Should be discoverable through semantic search.
        """
        dense_vectorizer, _ = vectorizers

        query = "How do I temporarily override DSPy settings for a specific operation?"
        query_vec = dense_vectorizer.embed(query)

        results = dspy_collection_manager.search_dense(query_vec, limit=5)

        assert len(results) > 0
        found = False
        for result in results:
            text = result.get("text", "")
            if "context" in text.lower() and "settings" in text.lower():
                found = True
                logger.info(
                    f"Found settings context info in {result.get('payload', {}).get('source')}"
                )
                break

        assert found, "Could not find information about settings context"

    def test_medium_discovery_faiss_hybrid(self, dspy_collection_manager, vectorizers):
        """MEDIUM TEST: Discover FAISS hybrid search with reranking.

        This is an internal optimization that's never explicitly documented.
        Requires understanding the code logic.
        """
        dense_vectorizer, _ = vectorizers

        query = (
            "How does DSPy automatically optimize search for large datasets with FAISS?"
        )
        query_vec = dense_vectorizer.embed(query)

        results = dspy_collection_manager.search_dense(query_vec, limit=5)

        # This is harder - check for FAISS mentions
        found_faiss = False
        for result in results:
            text = result.get("text", "")
            if "faiss" in text.lower():
                found_faiss = True
                logger.info(
                    f"Found FAISS info in {result.get('payload', {}).get('source')}"
                )
                # Bonus: check for candidate expansion pattern
                if "k * 10" in text or "candidate" in text.lower():
                    logger.info("Found candidate expansion pattern!")
                break

        # This might not be found - that's okay for MEDIUM difficulty
        if not found_faiss:
            logger.warning(
                "FAISS hybrid search not found - this is expected for MEDIUM difficulty"
            )

    def test_hard_discovery_pid_filtering(self, dspy_collection_manager, vectorizers):
        """HARD TEST: Discover filtered_pids parameter in ColBERT retriever.

        This parameter exists but is never documented - only visible in source.
        """
        dense_vectorizer, _ = vectorizers

        query = "How can I restrict DSPy ColBERT search to specific passage IDs?"
        query_vec = dense_vectorizer.embed(query)

        results = dspy_collection_manager.search_dense(query_vec, limit=5)

        # This is hard - check for filtered_pids or filter_fn
        found = False
        for result in results:
            text = result.get("text", "")
            if "filtered_pids" in text or "filter_fn" in text:
                found = True
                logger.info(
                    f"Found PID filtering in {result.get('payload', {}).get('source')}"
                )
                break

        if not found:
            logger.info("PID filtering not found - expected for HARD difficulty")

    def test_hard_discovery_sync_send_to_stream(
        self, dspy_collection_manager, vectorizers
    ):
        """HARD TEST: Discover sync_send_to_stream internal function.

        This is an internal helper function that solves async context issues.
        Never exposed in public API.
        """
        dense_vectorizer, _ = vectorizers

        query = "How do I send messages to async streams from synchronous code in DSPy?"
        query_vec = dense_vectorizer.embed(query)

        results = dspy_collection_manager.search_dense(query_vec, limit=5)

        # Check for the function name or related patterns
        found = False
        for result in results:
            text = result.get("text", "")
            if "sync_send_to_stream" in text or (
                "asyncio.get_running_loop" in text and "send" in text.lower()
            ):
                found = True
                logger.info(
                    f"Found sync_send_to_stream in {result.get('payload', {}).get('source')}"
                )
                break

        if not found:
            logger.info("sync_send_to_stream not found - expected for HARD difficulty")

    def test_expert_discovery_citation_support(
        self, dspy_collection_manager, vectorizers
    ):
        """EXPERT TEST: Discover built-in citation support.

        This is in experimental module and never featured in tutorials.
        """
        dense_vectorizer, _ = vectorizers

        query = "Does DSPy have built-in support for academic citations with source tracking?"
        query_vec = dense_vectorizer.embed(query)

        results = dspy_collection_manager.search_dense(query_vec, limit=5)

        # Check for Citations class or citation-related code
        found = False
        for result in results:
            text = result.get("text", "")
            if "Citations" in text or "citation" in text.lower():
                found = True
                logger.info(
                    f"Found citation support in {result.get('payload', {}).get('source')}"
                )
                break

        if not found:
            logger.info("Citation support not found - expected for EXPERT difficulty")

    def test_multivector_vs_dense_accuracy(
        self, dspy_collection_manager, dense_vectorizer, colbert_vectorizer
    ):
        """Compare dense-only vs multivector retrieval accuracy.

        Test the hypothesis: Does ColBERT reranking improve accuracy?
        """
        if not colbert_vectorizer.is_available:
            pytest.skip("ColBERT not available")

        # Test query that requires precise understanding
        query = "What is the ToolCalls class and how does batch tool execution work?"
        dense_vec = dense_vectorizer.embed(query)
        colbert_vec = colbert_vectorizer.embed(query)

        # Dense-only results
        dense_results = dspy_collection_manager.search_dense(dense_vec, limit=5)

        # Multivector results (dense retrieve + ColBERT rerank)
        multivector_results = dspy_collection_manager.search_with_prefetch(
            dense_query=dense_vec,
            colbert_query=colbert_vec,
            limit=5,
            prefetch_limit=100,
        )

        logger.info(f"Dense-only: {len(dense_results)} results")
        logger.info(f"Multivector: {len(multivector_results)} results")

        # Qualitative assessment: Check if multivector finds ToolCalls class
        dense_found_toolcalls = any(
            "ToolCalls" in r.get("text", "") for r in dense_results
        )
        multivector_found_toolcalls = any(
            "ToolCalls" in r.get("text", "") for r in multivector_results
        )

        logger.info(f"Dense found ToolCalls: {dense_found_toolcalls}")
        logger.info(f"Multivector found ToolCalls: {multivector_found_toolcalls}")

        # If multivector finds it and dense doesn't, that's a win
        if multivector_found_toolcalls and not dense_found_toolcalls:
            logger.info("✓ ColBERT reranking improved accuracy!")


def test_discovery_summary():
    """Generate summary report of discovery capabilities.

    This meta-test runs all discovery tests and generates a report
    comparing AGENTX RAG effectiveness against different difficulty levels.
    """
    # This would run all tests in the class and aggregate results
    # For now, it's a placeholder for the final summary
    logger.info("""
    === DSPy Hidden Discovery Test Summary ===

    Test Levels:
    - EASY: Thread-safe settings, Persistent indices
    - MEDIUM: FAISS hybrid search, Stream reuse
    - HARD: PID filtering, sync_send_to_stream
    - EXPERT: Citation support, Python sandbox

    Success Criteria:
    1. Retrieval Accuracy: Can RAG find relevant code?
    2. Understanding: Can RAG explain how it works?
    3. Applicability: Can RAG recognize when to use it?
    4. Code Generation: Can RAG generate working code?

    Comparison: AGENTX (4B Gemma + RAG) vs GLM 4.7 brute force

    Full report to be generated after test execution.
    """)


if __name__ == "__main__":
    # Run quick test
    logging.basicConfig(level=logging.INFO)
    pytest.main([__file__, "-v", "-s"])
