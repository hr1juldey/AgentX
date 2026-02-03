"""Session performance tracking for LangGraph routing decisions.

Tracks which agent routes worked well for which query types,
enabling adaptive routing decisions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class RouteOutcome(str, Enum):
    """Outcome of a routing decision."""

    GOOD = "good"
    AVERAGE = "average"
    BAD = "bad"


class RoutingStrategy(str, Enum):
    """Routing strategy suggestion."""

    SIMILAR = "similar"
    DIFFERENT = "different"
    AUGMENT = "augment"
    SHORTEN = "shorten"


@dataclass
class AgentStep:
    """Single step in an agent routing path."""

    agent_name: str
    duration_ms: int
    success: bool
    quality_score: float

    def __post_init__(self) -> None:
        """Validate quality score range."""
        if not 0.0 <= self.quality_score <= 1.0:
            raise ValueError(f"quality_score must be 0.0-1.0, got {self.quality_score}")


@dataclass
class SessionPerformance:
    """Performance record for a session's routing.

    LangGraph uses this to decide routing for future queries:
    - If route A→C→B gave good results, use similar routing
    - If route failed, try different pattern
    """

    performance_id: UUID = field(default_factory=uuid4)
    session_id: str = ""
    user_id: str = ""
    query: str = ""

    # Routing path taken
    route_taken: list[AgentStep] = field(default_factory=list)

    # Overall outcome
    overall_outcome: RouteOutcome = RouteOutcome.AVERAGE

    # Performance metrics
    total_duration_ms: int = 0
    avg_quality_score: float = 0.0

    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Calculate derived metrics."""
        if self.route_taken:
            self.total_duration_ms = sum(step.duration_ms for step in self.route_taken)
            if self.route_taken:
                self.avg_quality_score = sum(
                    step.quality_score for step in self.route_taken
                ) / len(self.route_taken)

    def get_agent_names(self) -> list[str]:
        """Get list of agent names in order."""
        return [step.agent_name for step in self.route_taken]

    def was_successful(self) -> bool:
        """Check if the route was successful."""
        return self.overall_outcome in (RouteOutcome.GOOD, RouteOutcome.AVERAGE)
