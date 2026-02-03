"""Pattern Storage for Search Term Pattern Service.

Manages in-memory storage of search term patterns and records.
"""

from typing import Optional

from agentx.core.config import get_settings
from agentx.domain.entities.search_term_pattern import (
    SearchTermPattern,
    SearchTermRecord,
    TopicType,
)

settings = get_settings()


class PatternStorage:
    """Storage manager for search term patterns.

    Uses in-memory storage. For production, this should
    be replaced with persistent storage (database).
    """

    def __init__(self) -> None:
        """Initialize the pattern storage."""
        # In-memory pattern storage (key: user_id:topic_type)
        self._patterns: dict[str, SearchTermPattern] = {}

        # In-memory record storage
        self._records: list[SearchTermRecord] = []

    def add_record(self, record: SearchTermRecord) -> None:
        """Add a search record to storage.

        Args:
            record: SearchTermRecord to add
        """
        self._records.append(record)

    def get_pattern(
        self, user_id: str, topic_type: TopicType
    ) -> SearchTermPattern | None:
        """Get pattern for user and topic.

        Args:
            user_id: User ID
            topic_type: Topic type

        Returns:
            SearchTermPattern if found, None otherwise
        """
        pattern_key = f"{user_id}:{topic_type.value}"
        return self._patterns.get(pattern_key)

    def save_pattern(
        self,
        user_id: str,
        topic_type: TopicType,
        search_terms: list[str],
        quality_score: float,
    ) -> SearchTermPattern:
        """Save or update a pattern.

        Args:
            user_id: User ID
            topic_type: Topic type
            search_terms: Search terms to store
            quality_score: Quality score for this success

        Returns:
            Saved SearchTermPattern
        """
        pattern_key = f"{user_id}:{topic_type.value}"

        if pattern_key in self._patterns:
            # Update existing pattern
            pattern = self._patterns[pattern_key]
            pattern.record_success(quality_score)

            # Merge search terms if not already present
            for term in search_terms:
                if term not in pattern.search_terms:
                    pattern.search_terms.append(term)
            return pattern
        else:
            # Create new pattern
            pattern = SearchTermPattern(
                user_id=user_id,
                topic_type=topic_type,
                search_terms=search_terms.copy(),
                success_count=1,
                avg_quality_score=quality_score,
            )
            self._patterns[pattern_key] = pattern
            return pattern

    def extract_patterns(
        self,
        user_id: str,
        topic_type: Optional[TopicType] = None,
    ) -> list[SearchTermPattern]:
        """Extract learned patterns for a user and topic.

        Args:
            user_id: User ID to filter patterns
            topic_type: Topic type to filter (optional, all topics if None)

        Returns:
            List of SearchTermPattern objects (high quality only)
        """
        patterns: list[SearchTermPattern] = []

        for pattern_key, pattern in self._patterns.items():
            # Check if pattern belongs to user
            if not pattern_key.startswith(f"{user_id}:"):
                continue

            # Check topic filter
            if topic_type is not None and pattern.topic_type != topic_type:
                continue

            # Only return high-quality patterns
            if pattern.is_high_quality():
                patterns.append(pattern)

        # Sort by avg_quality_score (highest first)
        patterns.sort(key=lambda p: p.avg_quality_score, reverse=True)

        return patterns


__all__ = ["PatternStorage"]
