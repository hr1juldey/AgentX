"""Memory manager for AGENTX agents.

Handles Mem0AI integration for persistent memory across sessions.
"""

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import dspy

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages persistent memory for agents using Mem0AI.

    Provides search and storage operations with graceful degradation
    if Mem0AI is unavailable.
    """

    def __init__(self, user_id: str) -> None:
        """Initialize the memory manager.

        Args:
            user_id: User identifier for memory isolation
        """
        from agentx.core.dependencies import get_mem0_client

        self.user_id = user_id
        self._get_mem0_client = get_mem0_client
        self._mem0_client: object | None = None

    def get_client(self) -> object | None:
        """Get Mem0AI client (lazy loading).

        Returns:
            Mem0Client instance or None if unavailable
        """
        if self._mem0_client is None:
            self._mem0_client = self._get_mem0_client()
        return self._mem0_client

    def search_memory(self, context: str, question: str) -> str:
        """Search Mem0AI for relevant context.

        Args:
            context: Existing context string
            question: User's question

        Returns:
            Enhanced context with memory results
        """
        mem0_client = self.get_client()
        if not mem0_client:
            return context

        try:
            # Try to detect if we're in an async context
            try:
                asyncio.get_running_loop()
                # In async context - use synchronous approach by running in executor
                import threading

                result: list[str] = []

                def _run_in_thread():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            memories = loop.run_until_complete(
                                mem0_client.search_memory(
                                    question, self.user_id, limit=5
                                )  # type: ignore[no-untyped-call]
                            )
                            result.extend(memories)
                        finally:
                            loop.close()
                    except Exception as e:
                        logger.error(f"Memory search in thread failed: {e}")

                thread = threading.Thread(target=_run_in_thread)
                thread.start()
                thread.join(timeout=5.0)

                memories = result

            except RuntimeError:
                # No running loop - use asyncio.run() directly
                memories = asyncio.run(
                    mem0_client.search_memory(question, self.user_id, limit=5)  # type: ignore[no-untyped-call]
                )

            if memories:
                memory_context = "\n".join(memories)
                if context:
                    return f"{context}\n\nRelevant memories:\n{memory_context}"
                return f"Relevant memories:\n{memory_context}"

        except Exception as e:
            logger.warning(f"Mem0AI search failed: {e}")

        return context

    def store_interaction(self, question: str, result: "dspy.Prediction") -> None:
        """Store interaction in Mem0AI.

        Args:
            question: User's question
            result: Agent's response prediction
        """
        mem0_client = self.get_client()
        if not mem0_client:
            return

        try:
            # Extract answer from prediction
            answer = result.get("answer", str(result))  # type: ignore[no-untyped-call]

            # Format interaction as text
            interaction_text = f"User: {question}\nAssistant: {answer}"

            # Try to store asynchronously (non-blocking)
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                # No running loop - use asyncio.run()
                asyncio.run(
                    mem0_client.store_memory(  # type: ignore[no-untyped-call]
                        text=interaction_text,
                        user_id=self.user_id,
                        metadata={"category": "conversation"},
                    )
                )
            else:
                # Running loop exists - schedule as background task
                asyncio.create_task(
                    mem0_client.store_memory(  # type: ignore[no-untyped-call]
                        text=interaction_text,
                        user_id=self.user_id,
                        metadata={"category": "conversation"},
                    )
                )

        except Exception as e:
            logger.warning(f"Mem0AI storage failed: {e}")
