# T400: Create LangGraph State Schemas

**Phase**: 4
**Estimated Time**: 30 minutes
**Dependencies**: T001
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/agent_runtime.md` - LangGraph state definitions
- `lld/incremental_release_plan.md` - Phase 4: State schemas

**Description**:
Creates TypedDict schemas for LangGraph state machines. Defines backend state (agent reasoning) and frontend state (UI visibility).

---

## Acceptance Criteria

**Passing Criteria**:
- agent/langgraph/states.py exists
- BackendLangGraphState defined
- FrontendLangGraphState defined
- All state fields typed correctly
- States can be imported

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/agent/langgraph/states.py && echo "State schemas exist"

# Verify import works
python3 -c "from agentx.agent.langgraph.states import BackendLangGraphState, FrontendLangGraphState; print('States OK')"
```

---

## Implementation Steps

### Step 1: Create LangGraph state schemas

Create file `agentx/agent/langgraph/states.py`:

```python
"""LangGraph state schemas for AGENTX."""

from typing import TypedDict, List, Dict, Any, Optional, Literal
from uuid import UUID


class AgentStatus(str):
    """Agent execution status."""

    IDLE = "idle"
    THINKING = "thinking"
    USING_TOOL = "using_tool"
    COMPLETED = "completed"
    FAILED = "failed"


class VisibilityState(str):
    """Chat UI visibility state."""

    CHAT_VISIBLE = "chat_visible"
    CHAT_MINIMIZED = "chat_minimized"
    CHAT_HIDDEN = "chat_hidden"


class ReasoningStep(TypedDict):
    """Single reasoning step."""

    step_number: int
    thought: str
    action: Optional[str]
    observation: Optional[str]
    timestamp: str


class ToolCall(TypedDict):
    """Tool execution record."""

    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[str]
    error: Optional[str]
    duration_ms: int
    timestamp: str


class UIComponentState(TypedDict):
    """UI component state."""

    component_id: str
    component_type: str
    visible: bool
    dismissed: bool
    data: Dict[str, Any]


class BackendLangGraphState(TypedDict):
    """Backend LangGraph state for agent reasoning.

    Tracks agent execution through reasoning, tool use, and answer generation.
    """

    session_id: str
    user_query: str
    conversation_history: List[Dict[str, str]]
    retrieved_context: str
    reasoning_steps: List[ReasoningStep]
    current_step: int
    tool_calls: List[ToolCall]
    agent_status: AgentStatus
    confidence_score: float
    should_continue: bool
    final_answer: Optional[str]
    error_message: Optional[str]


class FrontendLangGraphState(TypedDict):
    """Frontend LangGraph state for UI visibility and components.

    Tracks what UI elements are visible and their lifecycle.
    """

    session_id: str
    active_components: Dict[str, UIComponentState]
    visibility_state: VisibilityState
    focused_component_id: Optional[str]
    pending_forms: Dict[str, Dict[str, Any]]
    stream_queue: List[Dict[str, Any]]
    is_streaming: bool
    user_interrupt_requested: bool


class FormState(TypedDict):
    """Form state for interrupt handling."""

    form_id: str
    fields: Dict[str, Any]
    status: Literal["pending", "submitted", "cancelled"]
    submitted_at: Optional[str]
    data: Optional[Dict[str, Any]]
```

### Step 2: Create langgraph __init__.py

Create file `agentx/agent/langgraph/__init__.py`:

```python
"""LangGraph state machines and schemas."""

from agentx.agent.langgraph.states import (
    BackendLangGraphState,
    FrontendLangGraphState,
    AgentStatus,
    VisibilityState,
    ReasoningStep,
    ToolCall,
    UIComponentState,
    FormState,
)

__all__ = [
    "BackendLangGraphState",
    "FrontendLangGraphState",
    "AgentStatus",
    "VisibilityState",
    "ReasoningStep",
    "ToolCall",
    "UIComponentState",
    "FormState",
]
```

---

## Expected Failures & Countermeasures

### Failure: TypedDict import error

**Likelihood**: Low
**Symptoms**: `NameError: name 'TypedDict' is not defined`

**Countermeasures**:
1. Ensure Python 3.9+ is being used
2. Check typing module is imported
3. Use from __future__ import annotations if needed

**Recovery Time**: 2 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T001 directory structure changed
**Detection**: agentx/agent/langgraph/ directory missing
**Action**: Re-run T001 to ensure all directories exist

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: State field names change
**Prevention**: All state field names are LOCKED
**Mitigation**: Update all LangGraph nodes and edges
**Affected Tasks**: T401 (Backend State Machine), T402 (Frontend State Machine)

---

## Artifacts

**Files Created**:
- `agentx/agent/langgraph/states.py` (State schemas, LOCKED)
- `agentx/agent/langgraph/__init__.py` (Package marker)

**Locked APIs**:
- All state class names
- All state field names and types
- AgentStatus enum values
- VisibilityState enum values

---

## Quality Gates

**Quality Checks**:
- **Check**: State schemas file exists
  - Command: `test -f agentx/agent/langgraph/states.py && echo "OK"`
  - Expected: `OK`
  - Required: Yes

- **Check**: States can be imported
  - Command: `python3 -c "from agentx.agent.langgraph.states import BackendLangGraphState, FrontendLangGraphState; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. Backend state tracks agent execution (reasoning, tools, answer)
2. Frontend state tracks UI visibility and components
3. AgentStatus: IDLE → THINKING → USING_TOOL → COMPLETED/FAILED
4. VisibilityState: CHAT_VISIBLE → CHAT_MINIMIZED → CHAT_HIDDEN
5. States use TypedDict for LangGraph compatibility
6. All states have session_id for tracking

---

## Completion Checklist

- [ ] states.py created with all state schemas
- [ ] BackendLangGraphState defined
- [ ] FrontendLangGraphState defined
- [ ] Helper types defined (ReasoningStep, ToolCall, UIComponentState, FormState)
- [ ] Enum values defined (AgentStatus, VisibilityState)
- [ ] langgraph/__init__.py exports all states
- [ ] All states can be imported
- [ ] Ready for T401 (Backend State Machine)

---

**Task T400 is part of Phase 4: LangGraph State Machines**
**Locked APIs**: All state class names, field names, and types
