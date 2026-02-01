# Spec: Conditional Routing

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the conditional routing functions that navigate the dynamic graph.

**Success Criteria**:
- route_by_plan() directs based on task count
- should_continue_research() uses structured decision
- No text parsing for routing (enum-based)
- All paths validated

---

## 2. Scope

### In Scope

- route_by_plan() function
- should_continue_research() function
- Conditional edge wiring
- Routing decision enums

### Out of Scope

- Evaluator logic (covered by evaluator-optimizer spec)
- Send API (covered by send-api-workers spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CR-001 | route_by_plan MUST check task count | Must |
| FR-CR-002 | Zero tasks → direct_answer | Must |
| FR-CR-003 | Non-zero tasks → create_workers | Must |
| FR-CR-004 | should_continue_research MUST use enum | Must |

---

## 4. API Contract

```python
# agent/nodes/routing.py
from enum import Enum

class RoutingPath(str, Enum):
    """Graph routing paths."""
    DIRECT_ANSWER = "direct_answer"
    CREATE_WORKERS = "create_workers"
    CONTINUE = "continue"
    ADD_TASKS = "add_tasks"
    FINALIZE = "finalize"

def route_by_plan(state: AgentState) -> RoutingPath:
    """Route based on execution plan.

    Key insight: Zero tasks → direct answer (no Send API needed).

    Args:
        state: Current agent state

    Returns:
        RoutingPath: Which node to route to
    """
    plan = state["execution_plan"]

    # Filter out cached tasks (already loaded from Store)
    uncached_tasks = [t for t in plan.research_tasks if not t.cached]

    if len(uncached_tasks) == 0:
        return RoutingPath.DIRECT_ANSWER
    else:
        return RoutingPath.CREATE_WORKERS

def should_continue_research(state: AgentState) -> RoutingPath:
    """Route based on evaluator's STRUCTURED decision.

    NO TEXT PARSING - uses enum values directly.

    Args:
        state: Current agent state

    Returns:
        RoutingPath: Which action to take
    """
    decision = state.get("continuation_decision")
    iteration = state.get("current_iteration", 0)
    max_iterations = 5

    # Hard limit
    if iteration >= max_iterations:
        return RoutingPath.FINALIZE

    # Structured decision routing
    if decision.action == ActionType.CONTINUE_RESEARCH:
        return RoutingPath.CONTINUE
    elif decision.action == ActionType.ADD_TASKS:
        return RoutingPath.ADD_TASKS
    else:  # FINALIZE
        return RoutingPath.FINALIZE
```

---

## 5. Graph Wiring

```python
# agent/graph/dynamic_agent_graph.py

# Entry point routing
builder.add_conditional_edges(
    "query_planner",
    route_by_plan,
    {
        RoutingPath.DIRECT_ANSWER: "direct_answer",
        RoutingPath.CREATE_WORKERS: "assign_workers",
    }
)

# Evaluator routing
builder.add_conditional_edges(
    "evaluator",
    should_continue_research,
    {
        RoutingPath.CONTINUE: "assign_workers",
        RoutingPath.ADD_TASKS: "assign_workers",
        RoutingPath.FINALIZE: "synthesizer",
    }
)
```

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-CR-001 | Zero tasks → direct | Task count check |
| BR-CR-002 | Max 5 iterations | Hard limit |
| BR-CR-003 | No text parsing | Enum-based routing |

---

## 7. Acceptance Criteria

- [ ] route_by_plan() checks task count
- [ ] Zero tasks routes to direct_answer
- [ ] should_continue_research() uses enum
- [ ] Max 5 iterations enforced
- [ ] No text parsing in routing
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

| State | Expected Path |
|-------|---------------|
| 0 uncached tasks | direct_answer |
| 3 uncached tasks | create_workers |
| Iteration 6 (max) | finalize (hard limit) |
| High confidence | finalize (evaluator) |
| Low confidence, iter < 5 | continue |

---

**Next**: See `send-api-workers/spec.md` for Send API implementation.
