"""Routing performance node for LangGraph.

Records session performance and suggests routing strategies.
"""

from typing import Any

from agentx.application.services.routing_decision_service import RoutingDecisionService
from agentx.domain.entities.session_performance import (
    RouteOutcome,
    SessionPerformance,
)


# Singleton instance
_routing_service: RoutingDecisionService | None = None


def get_routing_decision_service() -> RoutingDecisionService:
    """Get singleton routing decision service."""
    global _routing_service
    if _routing_service is None:
        _routing_service = RoutingDecisionService()
    return _routing_service


async def routing_performance_node(state: dict[str, Any]) -> dict[str, Any]:
    """LangGraph node for recording and using routing performance.

    Args:
        state: Current graph state with session_id, user_id, query, etc.

    Returns:
        Updated state with routing_suggestion if available
    """
    service = get_routing_decision_service()

    session_id = state.get("session_id", "")
    user_id = state.get("user_id", "")
    query = state.get("query", "")

    # Record previous performance if available
    if "agent_steps" in state and "quality_score" in state:
        performance = SessionPerformance(
            session_id=session_id,
            user_id=user_id,
            query=query,
            route_taken=state.get("agent_steps", []),
            overall_outcome=_determine_outcome(state.get("quality_score", 0.5)),
        )
        await service.record_session_performance(session_id, performance)

    # Get routing suggestion for next steps
    suggestion = await service.suggest_routing(user_id, query)

    return {
        **state,
        "routing_suggestion": suggestion,
    }


def _determine_outcome(quality_score: float) -> RouteOutcome:
    """Determine route outcome from quality score."""
    if quality_score >= 0.7:
        return RouteOutcome.GOOD
    if quality_score >= 0.5:
        return RouteOutcome.AVERAGE
    return RouteOutcome.BAD
