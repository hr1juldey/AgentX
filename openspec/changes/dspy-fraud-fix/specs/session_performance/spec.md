# Spec: Session Performance Tracking

**Domain**: session_performance
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Enable LangGraph routing decisions based on session performance history. Track which agent sequences (routes) produced good/average/bad outcomes.

**Problem Statement**: LangGraph has no visibility into which routing patterns worked well in previous sessions, preventing adaptive routing.

**Success Criteria**: SessionPerformance entity tracks route_taken and overall_outcome; RoutingDecisionService suggests routing strategies.

---

## 2. Scope

### In Scope

- SessionPerformance entity tracking route_taken, overall_outcome
- AgentStep dataclass (agent_name, duration_ms, success, quality_score)
- RouteOutcome enum (GOOD, AVERAGE, BAD)
- RoutingDecisionService for suggesting strategies
- Routing strategies: "similar", "different", "augment", "shorten"

### Out of Scope

- Actual routing logic (handled by LangGraph)
- Route execution (handled by existing graph nodes)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-PERF-001 | SessionPerformance tracks session_id, user_id, query, route_taken, overall_outcome | Must |
| RF-PERF-002 | AgentStep captures agent_name, duration_ms, success, quality_score | Must |
| RF-PERF-003 | RouteOutcome enum: GOOD, AVERAGE, BAD | Must |
| RF-PERF-004 | RoutingDecisionService.suggest_routing() returns strategy | Must |
| RF-PERF-005 | Service records and retrieves session performance | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-PERF-001 | All files pass Ruff and Pyrefly | Must |
| NFR-PERF-002 | Absolute imports only | Must |
| NFR-PERF-003 | Under 100 lines per file | Must |

---

## 4. Data Model

```python
# agentx/domain/entities/session_performance.py
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from enum import Enum

class RouteOutcome(str, Enum):
    """Overall outcome of a routing sequence."""
    GOOD = "good"       # Route produced quality results
    AVERAGE = "average" # Route produced acceptable results
    BAD = "bad"         # Route failed or produced poor results

@dataclass
class AgentStep:
    """Single step in a routing sequence."""
    agent_name: str
    duration_ms: int
    success: bool
    quality_score: float  # 0.0 to 1.0

@dataclass
class SessionPerformance:
    """Performance record for a session's routing."""
    performance_id: UUID
    session_id: str
    user_id: str
    query: str
    route_taken: list[AgentStep]
    overall_outcome: RouteOutcome
    created_at: datetime

    def get_total_duration_ms(self) -> int:
        """Total duration for the route."""
        return sum(step.duration_ms for step in self.route_taken)

    def get_average_quality(self) -> float:
        """Average quality score across steps."""
        if not self.route_taken:
            return 0.0
        return sum(step.quality_score for step in self.route_taken) / len(self.route_taken)
```

---

## 5. API Contract

This spec defines domain entities and service. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-PERF-001 | GOOD outcome = average_quality >= 0.7 | RoutingDecisionService |
| BR-PERF-002 | BAD outcome = average_quality < 0.4 OR any step failed | RoutingDecisionService |
| BR-PERF-003 | "similar" strategy when previous GOOD | RoutingDecisionService |
| BR-PERF-004 | "different" strategy when previous BAD | RoutingDecisionService |

---

## 7. Acceptance Criteria

- [ ] SessionPerformance entity exists
- [ ] AgentStep dataclass exists
- [ ] RouteOutcome enum exists with 3 values
- [ ] RoutingDecisionService.suggest_routing() returns dict with "strategy" key
- [ ] Service can record and retrieve session performance
- [ ] All files use absolute imports
- [ ] All files pass: `ruff check` and `pyrefly check`
- [ ] Verification passes:
```python
from agentx.application.services.routing_decision_service import RoutingDecisionService
from agentx.domain.entities.session_performance import SessionPerformance, RouteOutcome, AgentStep

service = RoutingDecisionService()
perf = SessionPerformance(
    performance_id=UUID('12345678-1234-5678-1234-567812345678'),
    session_id='test123',
    user_id='user1',
    query='What are blueberries good for?',
    route_taken=[AgentStep('analyst', 100, True, 0.9)],
    overall_outcome=RouteOutcome.GOOD,
    created_at=datetime.now()
)
await service.record_session_performance('test123', perf)
suggestion = await service.suggest_routing('user1', 'Tell me about raspberries')
assert 'strategy' in suggestion
```

---

## 8. References

- **Plan**: `.claude/plans/golden-skipping-hedgehog.md` (Batch 0b)
- **Domain Model LLD**: `docs/engineering/lld/domain_model.md`

---

**Related Specs**:
- `specs/memory_guided_search/spec.md` - Uses performance for routing
