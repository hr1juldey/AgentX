# Spec: ui-message-reducer

**File**: `specs/ui-message-reducer/spec.md`

## 1.1 Purpose

Define the ui_message_reducer state management pattern that automatically tracks all UI state in LangGraph.

## 1.2 Scope

**In Scope**:
- ui_message_reducer configuration in LangGraph state
- State tracking for UI messages
- Automatic state updates (no manual state management)

**Out of Scope**:
- Manual state management (replaced by ui_message_reducer)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-UM-001 | LangGraph state MUST include ui field with ui_message_reducer | Must |
| FR-UM-002 | ui_message_reducer MUST automatically track all UI messages | Must |

## 1.4 Data Model

```python
from typing import Sequence, TypedDict, Annotated
from langgraph.graph.ui import ui_message_reducer, AnyUIMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]
```

## 1.5 Acceptance Criteria

- [ ] AgentState includes ui field with ui_message_reducer
- [ ] UI state automatically tracked
- [ ] Designer agent can access state.ui
