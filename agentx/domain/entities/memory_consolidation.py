"""Memory consolidation entity.

Locked from LLD: domain_model.md (memory consolidation)

Entity for memory consolidation operations.
Consolidates session memories to long-term storage.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Any, Dict


@dataclass
class MemoryConsolidationEntity:
    """Memory consolidation result.

    Returned after consolidating session memories to long-term storage.
    Tracks consolidation statistics and results.
    """

    session_id: UUID
    user_id: str
    consolidated_at: datetime
    memories_consolidated: int
    memories_discarded: int
    consolidation_summary: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses.

        Returns:
            dict with all entity fields
        """
        return {
            "session_id": str(self.session_id),
            "user_id": self.user_id,
            "consolidated_at": self.consolidated_at.isoformat(),
            "memories_consolidated": self.memories_consolidated,
            "memories_discarded": self.memories_discarded,
            "consolidation_summary": self.consolidation_summary,
        }
