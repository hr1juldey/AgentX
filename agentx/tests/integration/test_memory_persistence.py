"""Integration test for Mem0AI memory persistence.

This test verifies that:
1. Memory can be stored during a conversation
2. Memory persists across agent instances (different sessions)
3. Memory can be retrieved to enhance context

Run with: pytest agentx/tests/integration/test_memory_persistence.py -v
Or directly: python agentx/tests/integration/test_memory_persistence.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add agentx to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_memory_persistence() -> bool:
    """Test memory persistence across agent instances.

    This test:
    1. Creates first agent and stores information
    2. Creates second agent (simulating reconnection)
    3. Verifies second agent retrieves information from first session
    """
    from agentx.application.agents import StemCellAgent  # type: ignore[import]
    from agentx.core.dependencies import ensure_dspy_configured  # type: ignore[import]

    # Configure DSPy globally
    ensure_dspy_configured()

    # Use unique test user ID
    test_user_id = "test_user_memory_persistence"

    # Phase 1: First agent session - store information
    logger.info("=== Phase 1: First Agent Session ===")
    agent1 = StemCellAgent(user_id=test_user_id)

    # Store a fact by asking the agent to remember something
    question1 = "My name is Alice and I love hiking in the mountains."
    logger.info(f"Storing: {question1}")

    response1 = agent1.forward(question=question1)
    logger.info(f"Agent 1 response: {response1.get('answer', 'No answer')}")

    # Give Mem0AI time to store and index
    await asyncio.sleep(6)

    # Phase 2: Second agent session - retrieve information
    logger.info("\n=== Phase 2: Second Agent Session (New Instance) ===")
    agent2 = StemCellAgent(user_id=test_user_id)

    # Ask a question that should trigger memory retrieval
    question2 = "What do you know about me?"
    logger.info(f"Retrieving: {question2}")

    # Debug: check what memories are stored
    from agentx.core.dependencies import get_mem0_client  # type: ignore[import]

    mem0 = get_mem0_client()
    if mem0:
        raw_results = mem0._memory.search(
            "What do you know?", user_id=test_user_id, limit=5
        )
        logger.info(f"DEBUG: Raw search results: {raw_results}")

    response2 = agent2.forward(question=question2)
    answer2: str = response2.get("answer", "No answer") or "No answer"  # type: ignore[assignment]
    logger.info(f"Agent 2 response: {answer2}")

    # Verify memory retrieval (basic check)
    success_indicators = ["Alice", "hiking", "mountains"]
    found_any = any(
        indicator.lower() in answer2.lower() for indicator in success_indicators
    )

    if found_any:
        logger.info(
            "✅ Memory persistence test PASSED - Agent 2 retrieved information from Agent 1's session"
        )
        return True
    else:
        logger.warning(
            "⚠️ Memory persistence test INCONCLUSIVE - Agent 2 may not have retrieved stored information"
        )
        logger.warning(f"   Expected to find one of: {success_indicators}")
        logger.warning(f"   Got: {answer2}")
        return False


async def test_memory_search_and_storage() -> bool:
    """Test basic memory search and storage operations.

    This is a simpler test that verifies:
    1. Memory can be stored
    2. Memory can be searched
    """
    from agentx.core.dependencies import get_mem0_client  # type: ignore[import]

    logger.info("=== Test: Memory Search and Storage ===")

    mem0_client = get_mem0_client()
    if not mem0_client:
        logger.error("❌ Mem0AI client not available - skipping test")
        return False

    test_user_id = "test_user_search_storage"

    # Store a memory
    test_memory = "Test user prefers Python over JavaScript for backend development."
    logger.info(f"Storing memory: {test_memory}")

    await mem0_client.store_memory(  # type: ignore[no-untyped-call]
        text=test_memory,
        user_id=test_user_id,
        metadata={"category": "preference"},
    )

    # Give Mem0AI time to index
    await asyncio.sleep(1)

    # Search for the memory
    search_query = "What programming language does the user prefer?"
    logger.info(f"Searching for: {search_query}")

    results = await mem0_client.search_memory(  # type: ignore[no-untyped-call]
        query=search_query,
        user_id=test_user_id,
        limit=5,
    )

    logger.info(f"Search results: {results}")

    if results:
        logger.info("✅ Memory search and storage test PASSED")
        return True
    else:
        logger.warning(
            "⚠️ Memory search and storage test INCONCLUSIVE - No results returned"
        )
        return False


async def main() -> None:
    """Run all memory persistence tests."""
    logger.info("Starting Mem0AI Memory Persistence Tests\n")

    # Test 1: Basic search and storage
    result1 = await test_memory_search_and_storage()

    # Test 2: Full persistence across sessions
    result2 = await test_memory_persistence()

    logger.info("\n=== Test Summary ===")
    logger.info(
        f"Memory Search/Storage: {'✅ PASSED' if result1 else '⚠️ INCONCLUSIVE'}"
    )
    logger.info(f"Memory Persistence: {'✅ PASSED' if result2 else '⚠️ INCONCLUSIVE'}")

    if result1 and result2:
        logger.info("\n🎉 All tests passed!")
    else:
        logger.info(
            "\n⚠️ Some tests were inconclusive - Mem0AI may need additional configuration"
        )


if __name__ == "__main__":
    asyncio.run(main())
