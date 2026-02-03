"""Search Term Pattern Service for AGENTX.

Learns from successful searches to predict effective search terms
for future queries based on topic patterns.
"""

from typing import Optional

from agentx.domain.entities.search_term_pattern import (
    SearchTermPattern,
    SearchTermRecord,
    TopicType,
)


class SearchTermPatternService:
    """Service for learning and predicting search term patterns.

    Tracks successful search terms by topic and uses pattern
    matching to suggest terms for similar queries.
    """

    def __init__(self) -> None:
        """Initialize the search term pattern service.

        Uses in-memory storage. For production, this should
        be replaced with persistent storage (database).
        """
        # In-memory pattern storage (key: user_id:topic_type)
        self._patterns: dict[str, SearchTermPattern] = {}

        # In-memory record storage
        self._records: list[SearchTermRecord] = []

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
        # Only record high-quality searches
        if quality_score < 0.7:
            # Create record but mark as not successful
            record = SearchTermRecord(
                user_id=user_id,
                query=query,
                topic_type=topic_type,
                search_terms=search_terms,
                quality_score=quality_score,
                was_successful=False,
            )
            self._records.append(record)
            return record

        # Create successful record
        record = SearchTermRecord(
            user_id=user_id,
            query=query,
            topic_type=topic_type,
            search_terms=search_terms,
            quality_score=quality_score,
            was_successful=True,
        )
        self._records.append(record)

        # Update or create pattern
        pattern_key = f"{user_id}:{topic_type.value}"

        if pattern_key in self._patterns:
            # Update existing pattern
            pattern = self._patterns[pattern_key]
            pattern.record_success(quality_score)

            # Merge search terms if not already present
            for term in search_terms:
                if term not in pattern.search_terms:
                    pattern.search_terms.append(term)
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
            topic_type = self._detect_topic_type(query)

        # Find pattern for this topic
        pattern_key = f"{user_id}:{topic_type.value}"

        if pattern_key not in self._patterns:
            # No pattern found for this topic
            return []

        pattern = self._patterns[pattern_key]

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

    def _detect_topic_type(self, query: str) -> TopicType:
        """Auto-detect topic type from query.

        Args:
            query: The query to analyze

        Returns:
            Detected TopicType
        """
        query_lower = query.lower()

        # Health keywords
        health_keywords = [
            "health",
            "medical",
            "nutrition",
            "disease",
            "symptoms",
            "treatment",
            "drug",
            "medicine",
            "doctor",
            "hospital",
            "vitamin",
            "antioxidant",
        ]
        if any(keyword in query_lower for keyword in health_keywords):
            return TopicType.HEALTH

        # Finance keywords
        finance_keywords = [
            "money",
            "finance",
            "financial",
            "investment",
            "stock",
            "market",
            "price",
            "cost",
            "budget",
            "saving",
            "bank",
            "loan",
            "currency",
        ]
        if any(keyword in query_lower for keyword in finance_keywords):
            return TopicType.FINANCE

        # Technology keywords
        tech_keywords = [
            "technology",
            "software",
            "hardware",
            "computer",
            "programming",
            "code",
            "app",
            "application",
            "digital",
            "internet",
            "ai",
            "machine learning",
            "algorithm",
        ]
        if any(keyword in query_lower for keyword in tech_keywords):
            return TopicType.TECHNOLOGY

        # Science keywords
        science_keywords = [
            "science",
            "scientific",
            "research",
            "study",
            "experiment",
            "physics",
            "chemistry",
            "biology",
            "theory",
            "hypothesis",
            "discovery",
        ]
        if any(keyword in query_lower for keyword in science_keywords):
            return TopicType.SCIENCE

        # Travel keywords
        travel_keywords = [
            "travel",
            "trip",
            "vacation",
            "flight",
            "hotel",
            "destination",
            "tourist",
            "visit",
            "location",
            "city",
            "country",
        ]
        if any(keyword in query_lower for keyword in travel_keywords):
            return TopicType.TRAVEL

        # Default to GENERAL
        return TopicType.GENERAL


__all__ = [
    "SearchTermPatternService",
]
