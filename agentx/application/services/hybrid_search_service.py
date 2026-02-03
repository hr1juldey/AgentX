"""Hybrid Search Service for RAG + SearXNG search strategy decisions.

Intelligently decides between RAG-only, SearXNG-only, or hybrid search
based on query characteristics and domain analysis.

Decision Logic:
- Current events, predictions, niche topics → SearXNG_ONLY
- Well-established facts → RAG_ONLY
- Complex/contradicting queries → HYBRID
"""

from dataclasses import dataclass, field
from enum import Enum

import dspy

from agentx.agent.dspy_signatures.main_signatures import MainAgentSignature
from agentx.application.services.search_term_pattern_service import (
    SearchTermPatternService,
)


class SearchStrategy(str, Enum):
    """Search strategy for query processing."""

    RAG_ONLY = "rag_only"
    SEARXNG_ONLY = "searxng_only"
    HYBRID = "hybrid"


class QueryCharacteristics(str, Enum):
    """Characteristics of a user query."""

    CURRENT_EVENTS = "current_events"
    PREDICTIONS = "predictions"
    WELL_ESTABLISHED = "well_established"
    NICHE = "niche"
    CONTRADICTING = "contradicting"


@dataclass
class SearchDecision:
    """Decision result for search strategy."""

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
        self.analyzer = dspy.Predict(MainAgentSignature)

    async def decide_strategy(
        self,
        query: str,
        user_id: str = "default",
    ) -> SearchDecision:
        """Decide which search strategy to use for a query.

        Args:
            query: User's query
            user_id: User ID for personalization (default: "default")

        Returns:
            SearchDecision with strategy and reasoning
        """
        # Use DSPy to analyze query characteristics
        analysis = self._analyze_query(query)

        # Determine characteristics
        characteristics = self._identify_characteristics(query, analysis)

        # Decide strategy based on characteristics
        strategy = self._decide_strategy_from_characteristics(characteristics)

        # Generate reasoning
        reasoning = self._generate_reasoning(characteristics, strategy)

        return SearchDecision(
            strategy=strategy,
            characteristics=characteristics,
            reasoning=reasoning,
            confidence=0.8,  # Default confidence
            suggested_terms=[],
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
        # Use SearchTermPatternService to predict terms
        pattern_service = SearchTermPatternService()
        predicted = await pattern_service.predict_terms(query, user_id=user_id)
        return predicted

    def _analyze_query(self, query: str) -> dspy.Prediction:
        """Analyze query using DSPy (synchronous).

        Args:
            query: User's query

        Returns:
            DSPy Prediction with analysis
        """
        # Use DSPy to get query analysis (Predict is synchronous)
        result = self.analyzer(query=query)  # type: ignore[call-arg]
        return result  # type: ignore[return-value]

    def _identify_characteristics(
        self,
        query: str,
        analysis: dspy.Prediction,
    ) -> list[QueryCharacteristics]:
        """Identify characteristics of the query.

        Args:
            query: User's query
            analysis: DSPy analysis result

        Returns:
            List of identified characteristics
        """
        characteristics: list[QueryCharacteristics] = []
        query_lower = query.lower()

        # Check for current events indicators
        current_event_keywords = [
            "latest",
            "recent",
            "breaking",
            "today",
            "yesterday",
            "this week",
            "this month",
            "this year",
            "2024",
            "2025",
            "2026",
            "news",
            "happening",
        ]
        if any(keyword in query_lower for keyword in current_event_keywords):
            characteristics.append(QueryCharacteristics.CURRENT_EVENTS)

        # Check for prediction indicators
        prediction_keywords = [
            "will",
            "predict",
            "forecast",
            "future",
            "expect",
            "likely",
            "probability",
            "chance",
            "upcoming",
        ]
        if any(keyword in query_lower for keyword in prediction_keywords):
            characteristics.append(QueryCharacteristics.PREDICTIONS)

        # Check for well-established fact indicators
        established_keywords = [
            "what is",
            "define",
            "explain",
            "history",
            "capital of",
            "population of",
            "who was",
            "when did",
        ]
        if any(keyword in query_lower for keyword in established_keywords):
            characteristics.append(QueryCharacteristics.WELL_ESTABLISHED)

        # Check for niche/obscure topic indicators
        niche_keywords = [
            "obscure",
            "rare",
            "little known",
            "uncommon",
            "specialized",
            "technical",
        ]
        if any(keyword in query_lower for keyword in niche_keywords):
            characteristics.append(QueryCharacteristics.NICHE)

        # Check for contradicting/complex indicators
        contradicting_keywords = [
            "compare",
            "versus",
            "vs",
            "difference",
            "conflict",
            "contradiction",
            "debate",
            "controversy",
        ]
        if any(keyword in query_lower for keyword in contradicting_keywords):
            characteristics.append(QueryCharacteristics.CONTRADICTING)

        # If no characteristics identified, default to WELL_ESTABLISHED
        if not characteristics:
            characteristics.append(QueryCharacteristics.WELL_ESTABLISHED)

        return characteristics

    def _decide_strategy_from_characteristics(
        self,
        characteristics: list[QueryCharacteristics],
    ) -> SearchStrategy:
        """Decide search strategy based on identified characteristics.

        Args:
            characteristics: List of query characteristics

        Returns:
            SearchStrategy to use
        """
        # Priority 1: Contradicting queries need HYBRID
        if QueryCharacteristics.CONTRADICTING in characteristics:
            return SearchStrategy.HYBRID

        # Priority 2: Multiple characteristics suggest complexity → HYBRID
        if len(characteristics) >= 3:
            return SearchStrategy.HYBRID

        # Priority 3: Current events or predictions → SearXNG_ONLY
        if QueryCharacteristics.CURRENT_EVENTS in characteristics:
            return SearchStrategy.SEARXNG_ONLY
        if QueryCharacteristics.PREDICTIONS in characteristics:
            return SearchStrategy.SEARXNG_ONLY
        if QueryCharacteristics.NICHE in characteristics:
            return SearchStrategy.SEARXNG_ONLY

        # Priority 4: Well-established facts → RAG_ONLY
        if QueryCharacteristics.WELL_ESTABLISHED in characteristics:
            return SearchStrategy.RAG_ONLY

        # Default: HYBRID for safety
        return SearchStrategy.HYBRID

    def _generate_reasoning(
        self,
        characteristics: list[QueryCharacteristics],
        strategy: SearchStrategy,
    ) -> str:
        """Generate human-readable reasoning for the decision.

        Args:
            characteristics: Identified query characteristics
            strategy: Decided search strategy

        Returns:
            Human-readable reasoning string
        """
        char_names = [c.value for c in characteristics]
        reasoning = f"Query characteristics: {', '.join(char_names)}. "

        if strategy == SearchStrategy.SEARXNG_ONLY:
            reasoning += "Using SearXNG for current/external information."
        elif strategy == SearchStrategy.RAG_ONLY:
            reasoning += "Using RAG for well-established knowledge."
        else:  # HYBRID
            reasoning += "Using hybrid search for comprehensive coverage."

        return reasoning


__all__ = [
    "HybridSearchService",
    "SearchStrategy",
    "QueryCharacteristics",
    "SearchDecision",
]
