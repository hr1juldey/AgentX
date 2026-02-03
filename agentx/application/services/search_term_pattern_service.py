"""Search Term Pattern Service for AGENTX.

Learns from successful searches to predict effective search terms
for future queries based on topic patterns.
"""

from typing import Optional

from agentx.application.services.pattern_storage import PatternStorage
from agentx.application.services.topic_detector import TopicDetector
from agentx.core.config import get_settings
from agentx.domain.entities.search_term_pattern import (
    SearchTermPattern,
    SearchTermRecord,
    TopicType,
)

settings = get_settings()


class SearchTermPatternService:
    """Service for learning and predicting search term patterns.

    Tracks successful search terms by topic and uses pattern
    matching to suggest terms for similar queries.
    """

    def __init__(self) -> None:
        """Initialize the search term pattern service."""
        self.storage = PatternStorage()
        self.detector = TopicDetector()

    async def record_search(
        self,
        query: str,
        search_terms: list[str],
        quality_score: float,
        topic_type: TopicType,
        user_id: str = "default",
    ) -> SearchTermRecord:
        """Record a search execution for pattern learning.

        Only records searches with quality >= 0.7 to learn from
        successful patterns.

        Args:
            query: The query that was executed
            search_terms: Search terms that were used
            quality_score: Quality score of results (0.0-1.0)
            topic_type: Topic category for the query
            user_id: User ID for personalization (default: "default")

        Returns:
            SearchTermRecord that was created
        """
        # Create record
        was_successful = quality_score >= settings.memory.high_quality_threshold
        record = SearchTermRecord(
            user_id=user_id,
            query=query,
            topic_type=topic_type,
            search_terms=search_terms,
            quality_score=quality_score,
            was_successful=was_successful,
        )
        self.storage.add_record(record)

        # Only update patterns for successful searches
        if was_successful:
            self.storage.save_pattern(user_id, topic_type, search_terms, quality_score)

        return record

    async def predict_terms(
        self,
        query: str,
        user_id: str = "default",
        topic_type: Optional[TopicType] = None,
    ) -> list[str]:
        """Predict effective search terms for a query.

        Uses historical patterns to suggest search terms that
        have worked well for similar queries.

        Args:
            query: The query to predict terms for
            user_id: User ID for personalization (default: "default")
            topic_type: Topic type (optional, auto-detected if not provided)

        Returns:
            List of predicted search terms (empty if no patterns available)
        """
        # Auto-detect topic type if not provided
        if topic_type is None:
            topic_type = self.detector.detect(query)

        # Find pattern for this topic
        pattern = self.storage.get_pattern(user_id, topic_type)

        if pattern is None:
            return []

        # Only suggest terms from high-quality patterns
        if not pattern.is_high_quality():
            return []

        # Return the search terms from the pattern
        return pattern.search_terms.copy()

    async def extract_patterns(
        self,
        user_id: str = "default",
        topic_type: Optional[TopicType] = None,
    ) -> list[SearchTermPattern]:
        """Extract learned patterns for a user and topic.

        Args:
            user_id: User ID to filter patterns (default: "default")
            topic_type: Topic type to filter (optional, all topics if None)

        Returns:
            List of SearchTermPattern objects
        """
        return self.storage.extract_patterns(user_id, topic_type)


__all__ = [
    "SearchTermPatternService",
]
