"""Work-experience memory entities for AGENTX.

Agents remember their WORK (data, instructions, reasoning, output),
NOT facts/knowledge. This is critical for learning and routing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class WorkExperienceType(str, Enum):
    """Type of work experience memory."""

    DATA_INPUT = "data_input"
    INSTRUCTION_INPUT = "instruction_input"
    REASONING_DONE = "reasoning_done"
    OUTPUT_PRODUCED = "output_produced"
    TOOL_USED = "tool_used"
    ERROR_ENCOUNTERED = "error_encountered"


class SourceType(str, Enum):
    """Type of source for memory attribution (for conflict resolution)."""

    ACADEMIC = "academic"
    REPORT = "report"
    GENERAL = "general"
    SOCIAL = "social"
    UNKNOWN = "unknown"


@dataclass
class MemoryRecord:
    """Work-experience memory record.

    Agents remember WHAT THEY DID, not arbitrary facts.
    This enables learning, routing decisions, and quality-based retrieval.
    """

    memory_id: UUID = field(default_factory=uuid4)
    user_id: str = ""
    session_id: str = ""
    memory_type: WorkExperienceType = WorkExperienceType.OUTPUT_PRODUCED

    # What the agent received and did
    data_input: str = ""
    instruction_input: str = ""
    reasoning_done: str = ""
    output_produced: str = ""

    # Quality tracking
    quality_score: float = 0.8
    source_type: SourceType = SourceType.UNKNOWN
    confidence_score: float = 0.7

    # Memory lifecycle
    access_count: int = 0
    ttl_days: int = 30
    superseded_by: Optional[UUID] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if memory has expired based on TTL."""
        if self.superseded_by is not None:
            return True
        expiry_date = self.created_at + timedelta(days=self.ttl_days)
        return datetime.now() > expiry_date

    def record_access(self) -> None:
        """Record that this memory was accessed."""
        self.access_count += 1
        self.last_accessed_at = datetime.now()

    def extend_ttl(self, additional_days: int = 7) -> None:
        """Extend TTL (used by reinforcement tracker for good retrievals)."""
        self.ttl_days += additional_days

    def shorten_ttl(self, reduction_days: int = 7) -> None:
        """Shorten TTL (used by reinforcement tracker for bad retrievals)."""
        self.ttl_days = max(1, self.ttl_days - reduction_days)

    def is_reliable(self) -> bool:
        """Check if memory is reliable enough for reuse."""
        return (
            self.quality_score >= 0.7
            and self.confidence_score >= 0.6
            and not self.is_expired()
        )
