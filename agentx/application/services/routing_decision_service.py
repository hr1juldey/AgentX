"""Routing decision service for LangGraph adaptive routing.

Suggests routing strategies based on past session performance.
"""

from collections import defaultdict
from datetime import datetime, timedelta

from agentx.domain.entities.session_performance import (
    RouteOutcome,
    RoutingStrategy,
    SessionPerformance,
)


class RoutingDecisionService:
    """Service for making routing decisions based on history."""

    def __init__(self) -> None:
        self._history: list[SessionPerformance] = []
        self._user_performance: dict[str, list[SessionPerformance]] = defaultdict(list)

    async def record_session_performance(
        self,
        session_id: str,
        performance: SessionPerformance,
    ) -> None:
        """Record session performance for future routing."""
        self._history.append(performance)
        self._user_performance[performance.user_id].append(performance)

    async def suggest_routing(
        self,
        user_id: str,
        query: str,
        recent_hours: int = 24,
    ) -> dict[str, RoutingStrategy | list[str] | str]:
        """Suggest routing strategy based on past performance.

        Args:
            user_id: User to get history for
            query: Current query (for similarity matching)
            recent_hours: Only consider recent sessions

        Returns:
            Dict with strategy, suggested_route, and reasoning
        """
        user_history = self._user_performance.get(user_id, [])

        # Filter to recent sessions
        cutoff = datetime.now() - timedelta(hours=recent_hours)
        recent = [p for p in user_history if p.created_at > cutoff]

        if not recent:
            return {
                "strategy": RoutingStrategy.SIMILAR,
                "suggested_route": ["analyst", "researcher"],
                "reasoning": "No history - use default route",
            }

        # Analyze recent performance
        good_sessions = [p for p in recent if p.overall_outcome == RouteOutcome.GOOD]
        bad_sessions = [p for p in recent if p.overall_outcome == RouteOutcome.BAD]

        if len(good_sessions) > len(bad_sessions):
            # Recent routes working well - suggest similar
            best_session = max(good_sessions, key=lambda p: p.avg_quality_score)
            return {
                "strategy": RoutingStrategy.SIMILAR,
                "suggested_route": best_session.get_agent_names(),
                "reasoning": f"Recent route performed well (quality: {best_session.avg_quality_score:.2f})",
            }
        elif len(bad_sessions) > len(good_sessions):
            # Recent routes failing - suggest different
            return {
                "strategy": RoutingStrategy.DIFFERENT,
                "suggested_route": ["analyst", "synthesizer"],
                "reasoning": "Recent routes underperformed - try different pattern",
            }
        else:
            # Mixed results - suggest augmentation
            return {
                "strategy": RoutingStrategy.AUGMENT,
                "suggested_route": ["analyst", "researcher", "synthesizer"],
                "reasoning": "Mixed results - add more agents for robustness",
            }
