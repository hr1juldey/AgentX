"""Query Characteristic Analyzer for Hybrid Search.

Identifies characteristics of user queries to inform search strategy decisions.
"""

from dataclasses import dataclass
from enum import Enum

import dspy

from agentx.agent.dspy_signatures.main_signatures import MainAgentSignature
from agentx.application.services.search_strategy.query_keywords import (
    CONTRADICTING_KEYWORDS,
    CURRENT_EVENT_KEYWORDS,
    ESTABLISHED_KEYWORDS,
    NICHE_KEYWORDS,
    PREDICTION_KEYWORDS,
)


class QueryCharacteristics(str, Enum):
    """Characteristics of a user query."""

    CURRENT_EVENTS = "current_events"
    PREDICTIONS = "predictions"
    WELL_ESTABLISHED = "well_established"
    NICHE = "niche"
    CONTRADICTING = "contradicting"


@dataclass
class CharacteristicAnalysis:
    """Result of query characteristic analysis."""

    characteristics: list[QueryCharacteristics]
    reasoning: str = ""
    confidence: float = 0.0


class QueryCharacteristicAnalyzer:
    """Analyzes query characteristics to inform search strategy.

    Uses DSPy and keyword heuristics to identify:
    - Current events (recent, breaking news)
    - Predictions (future, speculation)
    - Well-established facts (definitions, history)
    - Niche topics (obscure, specialized)
    - Contradicting queries (compare, versus)
    """

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self.analyzer = dspy.Predict(MainAgentSignature)

    def analyze(self, query: str) -> CharacteristicAnalysis:
        """Analyze query characteristics.

        Args:
            query: User's query

        Returns:
            CharacteristicAnalysis with identified characteristics
        """
        # Use DSPy for initial analysis
        dspy_analysis = self._analyze_with_dspy(query)

        # Identify characteristics using heuristics
        characteristics = self._identify_characteristics(query, dspy_analysis)

        return CharacteristicAnalysis(
            characteristics=characteristics,
            reasoning=f"Identified {len(characteristics)} characteristics",
            confidence=0.8,
        )

    def _analyze_with_dspy(self, query: str) -> dspy.Prediction:
        """Analyze query using DSPy.

        Args:
            query: User's query

        Returns:
            DSPy Prediction with analysis
        """
        result = self.analyzer(query=query)  # type: ignore[call-arg]
        return result  # type: ignore[return-value]

    def _identify_characteristics(
        self, query: str, analysis: dspy.Prediction
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
        if any(keyword in query_lower for keyword in CURRENT_EVENT_KEYWORDS):
            characteristics.append(QueryCharacteristics.CURRENT_EVENTS)

        # Check for prediction indicators
        if any(keyword in query_lower for keyword in PREDICTION_KEYWORDS):
            characteristics.append(QueryCharacteristics.PREDICTIONS)

        # Check for well-established fact indicators
        if any(keyword in query_lower for keyword in ESTABLISHED_KEYWORDS):
            characteristics.append(QueryCharacteristics.WELL_ESTABLISHED)

        # Check for niche/obscure topic indicators
        if any(keyword in query_lower for keyword in NICHE_KEYWORDS):
            characteristics.append(QueryCharacteristics.NICHE)

        # Check for contradicting/complex indicators
        if any(keyword in query_lower for keyword in CONTRADICTING_KEYWORDS):
            characteristics.append(QueryCharacteristics.CONTRADICTING)

        # If no characteristics identified, default to WELL_ESTABLISHED
        if not characteristics:
            characteristics.append(QueryCharacteristics.WELL_ESTABLISHED)

        return characteristics


__all__ = [
    "QueryCharacteristicAnalyzer",
    "QueryCharacteristics",
    "CharacteristicAnalysis",
]
