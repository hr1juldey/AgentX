"""Search term pattern entities for AGENTX.

Tracks successful search term patterns by topic type to enable
intelligent search term prediction for future queries.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class TopicType(str, Enum):
    """Type of topic for search term pattern categorization."""

    HEALTH = "health"
    FINANCE = "finance"
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    TRAVEL = "travel"
    GENERAL = "general"


@dataclass
class SearchTermPattern:
    """Search term pattern for a specific topic.

    Tracks successful search terms that have worked well
    for queries in a specific topic domain.
    """

    pattern_id: UUID = field(default_factory=uuid4)
    user_id: str = ""
    topic_type: TopicType = TopicType.GENERAL

    # The search terms that worked well
    search_terms: list[str] = field(default_factory=list)

    # Success metrics
    success_count: int = 0
    avg_quality_score: float = 0.0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_used_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=datetime.now)

    def record_success(self, quality_score: float) -> None:
        """Record a successful use of this pattern.

        Args:
            quality_score: Quality score of the search result (0.0-1.0)
        """
        self.success_count += 1
        self.last_used_at = datetime.now()

        # Update average quality score
        if self.success_count == 1:
            self.avg_quality_score = quality_score
        else:
            # Rolling average
            self.avg_quality_score = (
                self.avg_quality_score * (self.success_count - 1) + quality_score
            ) / self.success_count

        self.updated_at = datetime.now()

    def is_high_quality(self) -> bool:
        """Check if this pattern is high quality."""
        return self.avg_quality_score >= 0.7 and self.success_count >= 2


@dataclass
class SearchTermRecord:
    """Record of a search execution for pattern learning.

    Tracks individual search executions to enable pattern
    extraction and learning over time.
    """

    record_id: UUID = field(default_factory=uuid4)
    user_id: str = ""

    # Query information
    query: str = ""
    topic_type: TopicType = TopicType.GENERAL

    # Search terms used
    search_terms: list[str] = field(default_factory=list)

    # Result quality
    quality_score: float = 0.0
    was_successful: bool = False

    # Timestamps
    executed_at: datetime = field(default_factory=datetime.now)

    def get_key_terms(self) -> list[str]:
        """Extract key terms from the search terms.

        Returns:
            List of key terms (filtered from common words)
        """
        common_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "with",
            "by",
        }

        key_terms: list[str] = []
        for term in self.search_terms:
            words = term.lower().split()
            filtered = [w for w in words if w not in common_words and len(w) > 2]
            key_terms.extend(filtered)

        return list(set(key_terms))


__all__ = [
    "TopicType",
    "SearchTermPattern",
    "SearchTermRecord",
]
