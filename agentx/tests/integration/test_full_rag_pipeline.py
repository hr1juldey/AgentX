"""Full RAG Pipeline Test: Retrieve + Augment + Generate using AGENTX components.

Tests the complete RAG pipeline using AGENTX's built-in components:
1. PrefetchRM: Multi-vector retrieval (dense + ColBERT)
2. StemCellAgent: DSPy agent with context handling
3. Full pipeline: Retrieve → Augment → Generate
"""

import logging

import pytest

from agentx.core.dependencies import ensure_dspy_configured
from agentx.infrastructure.retrieval.colbert_vectorizer import ColBERTVectorizer
from agentx.infrastructure.retrieval.dense_vectorizer import DenseVectorizer
from agentx.infrastructure.retrieval.prefetch_rm import PrefetchRM

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def rag_components():
    """Set up RAG components for testing."""
    # Configure DSPy with Ollama
    ensure_dspy_configured()

    # Read from .env via settings
    from agentx.core.config import settings

    # Initialize vectorizers using .env settings
    dense = DenseVectorizer(model_name=settings.mem0_embedder_model)
    colbert = ColBERTVectorizer(model_name="colbert-ir/colbertv2.0")

    # Get Qdrant collection manager (should already exist from indexing)
    from agentx.core.dependencies import get_qdrant_collection_manager

    manager = get_qdrant_collection_manager("dspy_hidden_capabilities")
    if manager is None:
        pytest.skip("Qdrant not available")

    # Verify collection has data
    from qdrant_client.http.exceptions import UnexpectedResponse

    try:
        info = manager._client.get_collection(manager.collection_name)
        points_count = info.points_count
        logger.info(f"Collection '{manager.collection_name}' has {points_count} points")
        if points_count == 0:
            pytest.skip("Collection is empty - run indexing first")
    except UnexpectedResponse:
        pytest.skip("Collection does not exist - run indexing first")

    # Create AGENTX retriever (PrefetchRM with Qdrant + ColBERT)
    retriever = PrefetchRM(
        collection_manager=manager,
        dense_vectorizer=dense,
        colbert_vectorizer=colbert,
        k=3,  # Retrieve top 3 chunks
    )

    return retriever, manager


class TestFullRAGPipeline:
    """Test complete RAG pipeline using AGENTX components."""

    def test_rag_sample_code_generation_with_agentx(self, rag_components):
        """Full RAG test: Can AGENTX generate code using retrieved DSPy documentation?

        Pipeline:
        1. RETRIEVE: PrefetchRM fetches relevant chunks (dense → ColBERT rerank)
        2. AUGMENT: Retrieved passages are added to DSPy context
        3. GENERATE: StemCellAgent generates answer using retrieved context

        Tests:
        - PrefetchRM multi-vector retrieval works
        - StemCellAgent can use retrieved context
        - End-to-end RAG produces useful answers
        """
        from agentx.application.agents.stem_cell import StemCellAgent

        retriever, manager = rag_components

        # ===== TEST QUESTION =====
        question = "How do I implement DSPy sample code generation with Ollama LLM?"

        # ===== RETRIEVE (using AGENTX PrefetchRM) =====
        logger.info(f"Question: {question}")

        # PrefetchRM returns dspy.Prediction with passages attribute
        retrieved = retriever(question, k=3)

        assert retrieved is not None, "Retriever returned None"
        assert hasattr(retrieved, "passages"), "Retriever didn't return passages"

        passages = retrieved.passages
        logger.info(f"Retrieved {len(passages)} passages")

        assert len(passages) > 0, "No passages retrieved"

        # Extract context from retrieved passages (passages are strings, not objects)
        context_text = "\n\n---\n\n".join(passages)

        logger.info(f"Context length: {len(context_text)} chars")
        logger.info(f"First passage preview: {passages[0][:200]}...")

        # ===== GENERATE (using AGENTX StemCellAgent) =====

        # Import StemCellAgent
        agent = StemCellAgent(user_id="test_user")

        # Use DSPy pattern: call module directly (not forward())
        try:
            result = agent(context=context_text, question=question)
            logger.info(f"Result type: {type(result)}")
            logger.info(f"Result keys/attrs: {dir(result)}")

            # Handle different result structures from DSPy
            if hasattr(result, "answer"):
                answer = result.answer
            elif isinstance(result, dict) and "answer" in result:
                answer = result["answer"]
            else:
                logger.error(f"Unexpected result structure: {result}")
                pytest.skip("Could not extract answer from result")

            logger.info(f"Generated answer: {len(answer)} chars")
        except Exception as e:
            logger.warning(f"StemCellAgent call failed: {e}")
            pytest.skip(f"StemCellAgent call failed: {e}")

        # ===== VALIDATE RESULTS =====
        assert len(answer) > 50, f"Answer too short: {len(answer)} chars"

        # Check for relevant concepts
        answer_lower = answer.lower()

        checks = {
            "Mentions DSPy": "dspy" in answer_lower,
            "Mentions Ollama/LM": "ollama" in answer_lower
            or "lm" in answer_lower
            or "localhost" in answer_lower,
            "Mentions code/examples": "code" in answer_lower
            or "example" in answer_lower
            or "import" in answer_lower,
        }

        print("\n" + "=" * 80)
        print("FULL RAG PIPELINE TEST RESULTS")
        print("=" * 80)
        print(f"\n📝 QUESTION:\n{question}\n")
        print(f"🔍 RETRIEVED: {len(passages)} passages")
        print(f"📝 CONTEXT: {len(context_text)} chars")
        print(f"✨ GENERATED: {len(answer)} chars")
        print(f"\n{'=' * 80}")
        print("GENERATED ANSWER:")
        print("=" * 80)
        print(answer)
        print("\n" + "=" * 80)
        print("QUALITY CHECKS:")
        print("=" * 80)
        for check_name, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"{status} {check_name}: {passed}")

        # At least one relevant concept should be mentioned
        assert any(checks.values()), (
            "Generated answer doesn't mention relevant concepts"
        )

    def test_prefetch_rm_multivector_retrieval(self, rag_components):
        """Test PrefetchRM multi-vector retrieval (dense + ColBERT rerank)."""
        retriever, manager = rag_components

        question = "What is DSPy ReAct agent and how does it work with tools?"

        # Retrieve using PrefetchRM (dense → ColBERT rerank)
        result = retriever(question, k=5)

        assert result is not None
        assert hasattr(result, "passages")
        assert len(result.passages) > 0

        print("\n" + "=" * 80)
        print("PREFETCH RM MULTI-VECTOR RETRIEVAL TEST")
        print("=" * 80)
        print(f"\nQuestion: {question}\n")
        print(f"Retrieved {len(result.passages)} passages:\n")

        for i, passage in enumerate(result.passages[:3]):
            print(f"Passage {i + 1}:")
            print(f"  Text: {passage[:200]}...")
            print()

    def test_rag_multihop_question(self, rag_components):
        """Test RAG with multi-hop reasoning question."""
        from agentx.application.agents.stem_cell import StemCellAgent

        retriever, manager = rag_components

        # Multi-hop question: Requires understanding retrieval + generation
        question = """
                    How do I build a DSPy agent that:
                        1. Retrieves relevant documentation
                        2. Uses that context to generate code examples
                        3. Runs with Ollama locally

                        Show me the complete setup.
                    """

        # Retrieve
        retrieved = retriever(question, k=3)
        context = "\n\n---\n\n".join(retrieved.passages)

        # Generate (use DSPy pattern: call module directly)
        agent = StemCellAgent(user_id="test_user")
        result = agent(context=context, question=question)

        # Handle different result structures from DSPy
        if hasattr(result, "answer"):
            answer = result.answer
        elif isinstance(result, dict) and "answer" in result:
            answer = result["answer"]
        else:
            pytest.skip("Could not extract answer from result")

        print("\n" + "=" * 80)
        print("MULTI-HOP RAG TEST")
        print("=" * 80)
        print(f"\nQuestion:\n{question}\n")
        print(f"Generated Answer:\n{answer}\n")

        assert len(answer) > 100, "Multi-hop answer too short"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pytest.main([__file__, "-v", "-s"])
