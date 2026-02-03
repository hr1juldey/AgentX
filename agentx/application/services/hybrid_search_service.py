"""Hybrid Search Service for RAG + SearXNG search strategy decisions.

Intelligently decides between RAG-only, SearXNG-only, or hybrid search
based on query characteristics and domain analysis.

Decision Logic:
- Current events, predictions, niche topics → SearXNG_ONLY
- Well-established facts → RAG_ONLY
- Complex/contradicting queries → HYBRID
"""

from dataclasses import dataclass, field

from agentx.application.services.query_characteristic_analyzer import (
    QueryCharacteristicAnalyzer,
    QueryCharacteristics,
)
from agentx.application.services.search_strategy_decider import (
    SearchStrategy,
    SearchStrategyDecider,
)
from agentx.application.services.search_term_pattern_service import (
    SearchTermPatternService,
)


@dataclass
class SearchDecisionWithTerms:
    """Extended search decision with suggested search terms."""

    strategy: SearchStrategy
    characteristics: list[QueryCharacteristics] = field(default_factory=list)
    reasoning: str = ""
    confidence: float = 0.0
    suggested_terms: list[str] = field(default_factory=list)


class HybridSearchService:
    """Service for deciding between RAG and SearXNG search strategies.

    Uses DSPy to analyze query characteristics and make intelligent
    decisions about which search strategy to use.

    Decision Logic:
    1. Current events (dates, recent events) → SearXNG_ONLY
    2. Predictions (future, speculation) → SearXNG_ONLY
    3. Niche topics (specific, obscure) → SearXNG_ONLY
    4. Well-established facts → RAG_ONLY
    5. Contradicting/complex queries → HYBRID
    """

    def __init__(self) -> None:
        """Initialize the hybrid search service."""
        self.analyzer = QueryCharacteristicAnalyzer()
        self.decider = SearchStrategyDecider()

    async def decide_strategy(
        self,
        query: str,
        user_id: str = "default",
    ) -> SearchDecisionWithTerms:
        """Decide which search strategy to use for a query.

        Args:
            query: User's query
            user_id: User ID for personalization (default: "default")

        Returns:
            SearchDecisionWithTerms with strategy, reasoning, and suggested terms
        """
        # Analyze query characteristics
        analysis = self.analyzer.analyze(query)

        # Decide strategy based on characteristics
        decision = self.decider.decide(analysis)

        # Get suggested search terms
        suggested_terms = await self._get_search_terms(query, user_id)

        return SearchDecisionWithTerms(
            strategy=decision.strategy,
            characteristics=decision.characteristics,
            reasoning=decision.reasoning,
            confidence=decision.confidence,
            suggested_terms=suggested_terms,
        )

    async def get_search_terms(
        self,
        query: str,
        user_id: str = "default",
    ) -> list[str]:
        """Get suggested search terms based on past patterns.

        Uses SearchTermPatternService to predict effective search terms
        based on historical patterns for similar queries.

        Args:
            query: User's query
            user_id: User ID for personalization (default: "default")

        Returns:
            List of suggested search terms
        """
        return await self._get_search_terms(query, user_id)

    async def _get_search_terms(
        self,
        query: str,
        user_id: str,
    ) -> list[str]:
        """Internal method to get search terms.

        Args:
            query: User's query
            user_id: User ID

        Returns:
            List of suggested search terms
        """
        # Use SearchTermPatternService to predict terms
        pattern_service = SearchTermPatternService()
        predicted = await pattern_service.predict_terms(query, user_id=user_id)
        return predicted


__all__ = [
    "HybridSearchService",
    "SearchStrategy",
    "QueryCharacteristics",
    "SearchDecisionWithTerms",
]
