# Spec: Send API Workers

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define dynamic worker creation using LangGraph Send API based on execution plan.

**Problem**: Fixed nodes can't adapt to query complexity.

**Success Criteria**:
- assign_workers() returns list[Send]
- Workers created dynamically from plan
- Dependencies respected
- Cycle detection prevents repeats

---

## 2. Scope

### In Scope

- assign_workers() routing function
- Send object creation for each ready task
- Dependency satisfaction checking
- Cycle detection

### Out of Scope

- Task execution implementation (covered by research-execution spec)
- Routing decisions (covered by conditional-routing spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SAW-001 | assign_workers MUST return list[Send] | Must |
| FR-SAW-002 | MUST respect task dependencies | Must |
| FR-SAW-003 | MUST detect cycles (visited tasks) | Must |
| FR-SAW-004 | MUST skip cached tasks | Must |

---

## 4. API Contract

```python
# agent/nodes/routing.py
from langgraph.types import Send
from typing import List

def assign_workers(state: AgentState) -> List[Send]:
    """Create DYNAMIC workers based on execution plan.

    This function is called by LangGraph's conditional edge.
    Returns a list of Send objects, each targeting research_worker node.

    Args:
        state: Current agent state

    Returns:
        list[Send]: One Send per ready task
    """
    plan = state["execution_plan"]
    visited = set(state.get("visited_tasks", []))

    # Find ready tasks: deps satisfied, not visited, not cached
    ready_tasks = [
        t for t in plan.research_tasks
        if not t.cached
        and all(dep in visited for dep in t.dependencies)
        and t.task_id not in visited
    ]

    # DYNAMIC worker creation - one Send per ready task
    return [
        Send(
            "research_worker",
            {"task": t, "session_id": state["session_id"]}
        )
        for t in ready_tasks
    ]
```

---

## 5. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-SAW-001 | No cached tasks | Filter t.cached == False |
| BR-SAW-002 | Deps satisfied | all(dep in visited) |
| BR-SAW-003 | No repeats | t.task_id not in visited |
| BR-SAW-004 | At least one worker | Empty list ends research |

---

## 6. Graph Integration

```python
# agent/graph/dynamic_agent_graph.py
from langgraph.graph import StateGraph

builder = StateGraph(AgentState)

# Add nodes
builder.add_node("assign_workers", assign_workers_node)
builder.add_node("research_worker", research_worker_node)

# Send API creates DYNAMIC workers
builder.add_conditional_edges(
    "assign_workers",
    assign_workers,  # Returns list[Send]
    ["research_worker"]  # Dynamic target
)
```

---

## 7. Acceptance Criteria

- [ ] assign_workers returns list[Send]
- [ ] Only ready tasks get workers
- [ ] Cached tasks skipped
- [ ] Dependencies respected
- [ ] Visited tasks not repeated
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

| Plan State | Visited | Expected Workers |
|------------|---------|------------------|
| 3 tasks, no deps | [] | 3 workers |
| 3 tasks, B depends on A | [A] | 1 worker (B) |
| All tasks cached | [] | 0 workers |
| Task already visited | [A] | 0 workers (A skipped) |

---

**Next**: See `conditional-routing/spec.md` for routing logic.
