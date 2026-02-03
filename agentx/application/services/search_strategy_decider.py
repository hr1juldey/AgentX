"""Search Strategy Decider for Hybrid Search.

Decides which search strategy to use based on query characteristics.
"""

from dataclasses import dataclass
from enum import Enum

from agentx.application.services.query_characteristic_analyzer import (
    CharacteristicAnalysis,
    QueryCharacteristics,
)


class SearchStrategy(str, Enum):
    """Search strategy for query processing."""

    RAG_ONLY = "rag_only"
    SEARXNG_ONLY = "searxng_only"
    HYBRID = "hybrid"


@dataclass
class SearchDecision:
    """Decision result for search strategy."""

    strategy: SearchStrategy
    characteristics: list[QueryCharacteristics]
    reasoning: str
    confidence: float = 0.8


class SearchStrategyDecider:
    """Decides search strategy based on query characteristics.

    Decision Logic:
    1. Contradicting queries → HYBRID
    2. Multiple characteristics (>=3) → HYBRID
    3. Current events or predictions → SEARXNG_ONLY
    4. Niche topics → SEARXNG_ONLY
    5. Well-established facts → RAG_ONLY
    6. Default → HYBRID (safe fallback)
    """

    def decide(self, analysis: CharacteristicAnalysis) -> SearchDecision:
        """Decide search strategy based on characteristics.

        Args:
            analysis: Characteristic analysis result

        Returns:
            SearchDecision with strategy and reasoning
        """
        characteristics = analysis.characteristics
        strategy = self._decide_strategy_from_characteristics(characteristics)
        reasoning = self._generate_reasoning(characteristics, strategy)

        return SearchDecision(
            strategy=strategy,
            characteristics=characteristics,
            reasoning=reasoning,
            confidence=analysis.confidence,
        )

    def _decide_strategy_from_characteristics(
        self, characteristics: list[QueryCharacteristics]
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

        # Priority 3: Current events or predictions → SEARXNG_ONLY
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
    "SearchStrategyDecider",
    "SearchStrategy",
    "SearchDecision",
]
