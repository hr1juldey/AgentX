"""Conflict Detection Module for RAG Conflict Resolution.

Provides logic for detecting conflicts between multiple memories
by comparing outputs and topic similarity.
"""

from agentx.domain.entities.memory_record import MemoryRecord


class ConflictDetector:
    """Detects conflicts between memories.

    Uses heuristics to identify potentially contradictory information:
    - Similar topics (based on input overlap)
    - Different outputs for similar inputs
    """

    def detect_conflicts(
        self, memories: list[MemoryRecord]
    ) -> list[tuple[MemoryRecord, MemoryRecord]]:
        """Detect conflicts between memories by comparing outputs.

        Args:
            memories: List of memories to check for conflicts

        Returns:
            List of conflict pairs (mem1, mem2)
        """
        conflicts: list[tuple[MemoryRecord, MemoryRecord]] = []

        for i, mem1 in enumerate(memories):
            for mem2 in memories[i + 1 :]:
                # Check if memories are about similar topics
                if self._similar_topics(mem1, mem2):
                    # Check if outputs differ significantly
                    if self._outputs_differ(mem1.output_produced, mem2.output_produced):
                        conflicts.append((mem1, mem2))

        return conflicts

    def _similar_topics(self, mem1: MemoryRecord, mem2: MemoryRecord) -> bool:
        """Check if two memories are about similar topics.

        Args:
            mem1: First memory
            mem2: Second memory

        Returns:
            True if topics are similar
        """
        # Check for exact matches in input fields
        if (
            mem1.data_input.strip().lower() == mem2.data_input.strip().lower()
            or mem1.instruction_input.strip().lower()
            == mem2.instruction_input.strip().lower()
        ):
            return True

        # Simple word overlap heuristic (can be enhanced with embeddings)
        words1 = set(mem1.data_input.lower().split())
        words2 = set(mem2.data_input.lower().split())
        overlap = len(words1 & words2) / max(len(words1), len(words2), 1)
        return overlap > 0.3

    def _outputs_differ(self, output1: str, output2: str) -> bool:
        """Check if two outputs differ significantly.

        Args:
            output1: First output
            output2: Second output

        Returns:
            True if outputs differ
        """
        # Simple heuristic: outputs are not identical
        return output1.strip().lower() != output2.strip().lower()


__all__ = ["ConflictDetector"]
