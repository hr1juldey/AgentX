# Spec: State Accumulation

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the state accumulation pattern that enables state-driven routing decisions.

**Problem**: R014 doesn't accumulate findings, so it "forgets why it searched."

**Success Criteria**:
- AgentState has accumulated_findings with reducer
- AgentState has accumulated_confidence
- AgentState has information_gaps with reducer
- Evaluator uses accumulated state

---

## 2. Scope

### In Scope

- AgentState TypedDict with reducers
- Accumulated state fields
- Reducer functions for lists

### Out of Scope

- Evaluator implementation (covered by evaluator-optimizer spec)
- Checkpointers (covered by checkpointers-integration spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SA-001 | AgentState MUST use Annotated with add reducer | Must |
| FR-SA-002 | research_findings MUST accumulate across iterations | Must |
| FR-SA-003 | information_gaps MUST accumulate across iterations | Must |
| FR-SA-004 | accumulated_confidence MUST be float (not list) | Should |

---

## 4. Data Model

```python
# domain/models/graph_state.py
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from operator import add

class AgentState(TypedDict):
    """Shared state for state-driven routing.

    Key insight: State ACCUMULATES across iterations.
    The evaluator reads this accumulated state to decide "what do I know?"
    """

    # Input
    messages: Annotated[list, add_messages]
    query: str
    user_id: str
    session_id: str
    input_path: InputPath  # TEXT or STT
    preprocessed_query: str | None

    # Execution plan
    execution_plan: ExecutionPlan
    current_iteration: int

    # 🔴 ACCUMULATED STATE (for state-driven decisions)
    research_findings: Annotated[list[str], add]  # ← Accumulates!
    research_sources: Annotated[list[str], add]  # ← Accumulates!
    task_results: dict[str, str]  # {task_id: result}
    information_gaps: Annotated[list[str], add]  # ← Accumulates!

    # State for evaluator decisions
    accumulated_confidence: float  # ← Increases with each finding
    research_quality: ResearchQuality | None  # LLM's assessment

    # Execution tracking
    visited_tasks: list[str]  # Tasks executed (not accumulated)
    execution_path: Annotated[list[str], add]  # Nodes visited

    # Output
    final_response: str | None
    selected_widgets: list[WidgetSpecification]  # For UI
```

---

## 5. Reducer Functions

```python
# LangGraph provides built-in reducers
from operator import add
from langgraph.graph.message import add_messages

# Usage in AgentState:
# - list[str] with add: Concatenates lists
# - add_messages: Appends messages (LangGraph special)
```

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-SA-001 | Findings always grow | Annotated[list[str], add] |
| BR-SA-002 | Confidence never decreases | max(old, new) logic |
| BR-SA-003 | Gaps tracked | Annotated[list[str], add] |
| BR-SA-004 | Visited not accumulated | Plain list (no reducer) |

---

## 7. Accumulation Example

```python
# Iteration 1
state_1 = {
    "research_findings": ["iPhone has 48MP camera"],
    "accumulated_confidence": 0.3,
    "information_gaps": ["Need Pixel info"],
}

# Iteration 2 (accumulator adds to previous)
state_2 = {
    # ACCUMULATED from previous + new
    "research_findings": [
        "iPhone has 48MP camera",  # From iteration 1
        "Pixel has 50MP camera",  # New
    ],
    "accumulated_confidence": 0.6,  # max(0.3, 0.6)
    "information_gaps": [
        "Need Pixel info",  # From iteration 1
        "Need comparison",  # New
    ],
}
```

---

## 8. Acceptance Criteria

- [ ] AgentState uses Annotated with add for lists
- [ ] research_findings accumulates
- [ ] information_gaps accumulates
- [ ] accumulated_confidence is float (not list)
- [ ] visited_tasks does NOT accumulate
- [ ] Pyrefly type checking passes

---

## 9. Test Scenarios

| Iterations | Expected research_findings | Expected confidence |
|------------|---------------------------|-------------------|
| 1 | [finding1] | 0.3 |
| 2 | [finding1, finding2] | max(0.3, 0.5) = 0.5 |
| 3 | [finding1, finding2, finding3] | max(0.5, 0.8) = 0.8 |

---

**Next**: See `evaluator-optimizer/spec.md` for how evaluator uses accumulated state.
