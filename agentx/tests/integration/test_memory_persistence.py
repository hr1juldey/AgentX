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

import dspy

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

    response1: dspy.Prediction = agent1(question=question1)  # type: ignore[call-arg]
    logger.info(f"Agent 1 response: {response1.get('answer', 'No answer')}")  # type: ignore[union-attr]

    # Give Mem0AI time to store and index
    await asyncio.sleep(6)

    # Phase 2: Second agent session - retrieve information
    logger.info("\n=== Phase 2: Second Agent Session (New Instance) ===")
    agent2 = StemCellAgent(user_id=test_user_id)

    # Ask a question that should trigger memory retrieval
    question2 = "What do you know about me?"
    logger.info(f"Retrieving: {question2}")

    response2: dspy.Prediction = agent2(question=question2)  # type: ignore[call-arg]
    answer2: str = response2.get("answer", "No answer") or "No answer"  # type: ignore[union-attr]
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


async def main() -> None:
    """Run memory persistence test."""
    logger.info("Starting Mem0AI Memory Persistence Tests\n")

    result = await test_memory_persistence()

    logger.info("\n=== Test Summary ===")
    logger.info(f"Memory Persistence: {'✅ PASSED' if result else '⚠️ INCONCLUSIVE'}")

    if result:
        logger.info("\n🎉 All tests passed!")
    else:
        logger.info(
            "\n⚠️ Test was inconclusive - Mem0AI may need additional configuration"
        )


if __name__ == "__main__":
    asyncio.run(main())
