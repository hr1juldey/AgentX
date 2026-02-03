"""Topic Detector for Search Term Pattern Service.

Auto-detects topic type from query keywords.
"""

from agentx.application.services.search_patterns.topic_keywords import (
    FINANCE_KEYWORDS,
    HEALTH_KEYWORDS,
    SCIENCE_KEYWORDS,
    TECH_KEYWORDS,
    TRAVEL_KEYWORDS,
)
from agentx.domain.entities.search_term_pattern import TopicType


class TopicDetector:
    """Detects topic type from query keywords.

    Checks for keywords associated with different topic types:
    - Health (medical, nutrition, symptoms)
    - Finance (money, investment, market)
    - Technology (software, programming, ai)
    - Science (research, physics, biology)
    - Travel (vacation, flight, hotel)
    - General (default)
    """

    def detect(self, query: str) -> TopicType:
        """Auto-detect topic type from query.

        Args:
            query: The query to analyze

        Returns:
            Detected TopicType
        """
        query_lower = query.lower()

        # Check health keywords
        if any(keyword in query_lower for keyword in HEALTH_KEYWORDS):
            return TopicType.HEALTH

        # Check finance keywords
        if any(keyword in query_lower for keyword in FINANCE_KEYWORDS):
            return TopicType.FINANCE

        # Check technology keywords
        if any(keyword in query_lower for keyword in TECH_KEYWORDS):
            return TopicType.TECHNOLOGY

        # Check science keywords
        if any(keyword in query_lower for keyword in SCIENCE_KEYWORDS):
            return TopicType.SCIENCE

        # Check travel keywords
        if any(keyword in query_lower for keyword in TRAVEL_KEYWORDS):
            return TopicType.TRAVEL

        # Default to GENERAL
        return TopicType.GENERAL


__all__ = ["TopicDetector"]
