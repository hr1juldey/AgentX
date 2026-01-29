"""Memory service for consolidation operations.

Handles memory consolidation from C005 (memory-rag).
Following the infrastructure pattern from mimicus.
"""

from uuid import UUID
from datetime import datetime

from agentx.domain.entities.memory_consolidation import MemoryConsolidationEntity
from agentx.domain.entities.enums import MemoryType
from agentx.domain.repositories.memory_repository import MemoryRepository


class MemoryService:
    """Service for memory consolidation operations.

    Handles:
    - Session memory consolidation
    - Memory retrieval and ranking
    - Fact invalidation (temporal RAG)
    """

    def __init__(self, memory_repository: MemoryRepository) -> None:
        """Initialize the memory service.

        Args:
            memory_repository: Memory repository instance.
        """
        self._memory_repository = memory_repository

    async def consolidate_session_memories(
        self,
        session_id: UUID,
        user_id: str,
    ) -> MemoryConsolidationEntity:
        """Consolidate session memories to long-term storage.

        Implements multi-hop agentic RAG pattern from C005:
        1. Retrieve episodic memories (conversation history)
        2. Extract semantic memories (facts, preferences)
        3. Rank and filter by relevance
        4. Store to long-term (Mem0AI)
        5. Return consolidation result

        Args:
            session_id: Session to consolidate.
            user_id: User identifier.

        Returns:
            MemoryConsolidationEntity: Consolidation result with statistics.
        """
        # Step 1: Retrieve episodic memories
        episodic_memories = await self._memory_repository.get_session_history(
            session_id
        )

        # Step 2: Extract semantic memories (facts, preferences)
        semantic_memories = []
        discarded_count = 0

        for memory in episodic_memories:
            # Extract facts and preferences
            extracted = self._extract_semantic_memory(memory)
            if extracted and self._is_consolidation_worthy(extracted):
                semantic_memories.append(extracted)
            else:
                discarded_count += 1

        # Step 3: Rank and filter by relevance
        ranked_memories = await self._rank_memories(semantic_memories)

        # Step 4: Store to long-term (Mem0AI)
        for memory in ranked_memories[:10]:  # Top 10 memories
            await self._memory_repository.store(
                memory_type=MemoryType.SEMANTIC,
                content=memory["content"],
                metadata={"timestamp": memory["timestamp"]},
                session_id=session_id,
            )

        # Step 5: Return consolidation result
        return MemoryConsolidationEntity(
            session_id=session_id,
            user_id=user_id,
            consolidated_at=datetime.now(),
            memories_consolidated=len(ranked_memories[:10]),
            memories_discarded=discarded_count,
            consolidation_summary=f"Consolidated {len(ranked_memories[:10])} memories, discarded {discarded_count}",
        )

    def _extract_semantic_memory(self, episodic_memory: dict) -> dict | None:
        """Extract semantic memory from episodic memory.

        Args:
            episodic_memory: Episodic memory from session.

        Returns:
            dict | None: Extracted semantic memory or None.
        """
        # In full implementation, would use DSPy agent for extraction
        content = episodic_memory.get("content", "")
        if not content:
            return None
        return {
            "content": content,
            "type": "semantic",
            "timestamp": episodic_memory.get("timestamp", datetime.now().isoformat()),
        }

    def _is_consolidation_worthy(self, memory: dict) -> bool:
        """Check if memory is worth consolidating.

        Args:
            memory: Memory to evaluate.

        Returns:
            bool: True if memory should be consolidated.
        """
        # Filter out low-value memories
        content = memory.get("content", "")
        return len(content) > 10 and "error" not in content.lower()

    async def _rank_memories(self, memories: list[dict]) -> list[dict]:
        """Rank memories by relevance.

        Args:
            memories: List of memories to rank.

        Returns:
            list[dict]: Ranked memories.
        """
        # In full implementation, would use vector similarity scoring
        # For now, return as-is (order preserved)
        return memories
