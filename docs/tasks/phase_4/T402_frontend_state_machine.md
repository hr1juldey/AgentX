# T402: Create Frontend State Machine

**Phase**: 4
**Estimated Time**: 40 minutes
**Dependencies**: T001, T400, T302
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/agent_runtime.md` - Frontend LangGraph state machine
- `lld/incremental_release_plan.md` - Phase 4: Frontend state machine

**Description**:
Creates LangGraph state machine for frontend UI visibility. Manages chat visibility, component lifecycle, and form interrupts.

---

## Acceptance Criteria

**Passing Criteria**:
- agent/langgraph/frontend_state_machine.py exists
- Manages UI component lifecycle
- Handles chat visibility state
- Supports form interrupt/resume
- Can be imported and instantiated

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/agent/langgraph/frontend_state_machine.py && echo "Frontend state machine exists"

# Verify import works
python3 -c "from agentx.agent.langgraph.frontend_state_machine import FrontendStateMachine; print('Import OK')"
```

---

## Implementation Steps

### Step 1: Create frontend state machine

Create file `agentx/agent/langgraph/frontend_state_machine.py`:

```python
"""Frontend LangGraph state machine for UI visibility."""

from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from agentx.agent.langgraph.states import (
    FrontendLangGraphState,
    VisibilityState,
    UIComponentState,
    FormState,
)
from agentx.ui.descriptors import UIDescriptorType


class FrontendStateMachine:
    """LangGraph state machine for frontend UI management.

    This state machine manages:
    1. UI component lifecycle (create → update → dismiss)
    2. Chat visibility (visible → minimized → hidden)
    3. Form interrupts (pause agent → submit → resume)
    4. Component focus management

    Example:
        >>> machine = FrontendStateMachine()
        >>> state = await machine.create_component("session-1", descriptor)
    """

    def __init__(self):
        """Initialize state machine."""
        self.states: Dict[str, FrontendLangGraphState] = {}

    def get_state(self, session_id: str) -> FrontendLangGraphState:
        """Get or create state for session.

        Args:
            session_id: Session identifier

        Returns:
            Frontend state for session
        """
        if session_id not in self.states:
            self.states[session_id] = self._create_initial_state(session_id)
        return self.states[session_id]

    def _create_initial_state(self, session_id: str) -> FrontendLangGraphState:
        """Create initial frontend state.

        Args:
            session_id: Session identifier

        Returns:
            Initial state
        """
        return {
            "session_id": session_id,
            "active_components": {},
            "visibility_state": VisibilityState.CHAT_VISIBLE,
            "focused_component_id": None,
            "pending_forms": {},
            "stream_queue": [],
            "is_streaming": False,
            "user_interrupt_requested": False,
        }

    async def create_component(
        self,
        session_id: str,
        descriptor: Dict[str, Any]
    ) -> FrontendLangGraphState:
        """Create UI component.

        Args:
            session_id: Session identifier
            descriptor: UI descriptor data

        Returns:
            Updated state
        """
        state = self.get_state(session_id)
        component_id = descriptor.get("descriptor_id", str(UUID.uuid4()))

        component_state: UIComponentState = {
            "component_id": component_id,
            "component_type": descriptor.get("descriptor_type"),
            "visible": True,
            "dismissed": False,
            "data": descriptor
        }

        state["active_components"][component_id] = component_state
        return state

    async def update_component(
        self,
        session_id: str,
        component_id: str,
        updates: Dict[str, Any]
    ) -> FrontendLangGraphState:
        """Update UI component.

        Args:
            session_id: Session identifier
            component_id: Component to update
            updates: Fields to update

        Returns:
            Updated state

        Raises:
            ValueError: If component not found
        """
        state = self.get_state(session_id)

        if component_id not in state["active_components"]:
            raise ValueError(f"Component {component_id} not found")

        state["active_components"][component_id]["data"].update(updates)
        return state

    async def dismiss_component(
        self,
        session_id: str,
        component_id: str
    ) -> FrontendLangGraphState:
        """Dismiss UI component.

        Args:
            session_id: Session identifier
            component_id: Component to dismiss

        Returns:
            Updated state
        """
        state = self.get_state(session_id)

        if component_id in state["active_components"]:
            state["active_components"][component_id]["visible"] = False
            state["active_components"][component_id]["dismissed"] = True

        return state

    async def set_chat_visibility(
        self,
        session_id: str,
        visibility: VisibilityState
    ) -> FrontendLangGraphState:
        """Set chat UI visibility.

        Args:
            session_id: Session identifier
            visibility: New visibility state

        Returns:
            Updated state
        """
        state = self.get_state(session_id)
        state["visibility_state"] = visibility
        return state

    async def focus_component(
        self,
        session_id: str,
        component_id: str
    ) -> FrontendLangGraphState:
        """Focus a component.

        Args:
            session_id: Session identifier
            component_id: Component to focus

        Returns:
            Updated state
        """
        state = self.get_state(session_id)
        state["focused_component_id"] = component_id
        return state

    async def start_form_interrupt(
        self,
        session_id: str,
        form_id: str,
        form_data: Dict[str, Any]
    ) -> FrontendLangGraphState:
        """Start form interrupt (pause agent).

        Args:
            session_id: Session identifier
            form_id: Form identifier
            form_data: Form fields

        Returns:
            Updated state
        """
        state = self.get_state(session_id)

        form_state: FormState = {
            "form_id": form_id,
            "fields": form_data,
            "status": "pending",
            "submitted_at": None,
            "data": None
        }

        state["pending_forms"][form_id] = form_state
        state["user_interrupt_requested"] = True
        return state

    async def submit_form(
        self,
        session_id: str,
        form_id: str,
        form_values: Dict[str, Any]
    ) -> FrontendLangGraphState:
        """Submit form (resume agent).

        Args:
            session_id: Session identifier
            form_id: Form identifier
            form_values: Submitted values

        Returns:
            Updated state
        """
        state = self.get_state(session_id)

        if form_id in state["pending_forms"]:
            state["pending_forms"][form_id]["status"] = "submitted"
            state["pending_forms"][form_id]["submitted_at"] = datetime.utcnow().isoformat()
            state["pending_forms"][form_id]["data"] = form_values
            state["user_interrupt_requested"] = False

        return state

    async def cancel_form(
        self,
        session_id: str,
        form_id: str
    ) -> FrontendLangGraphState:
        """Cancel form.

        Args:
            session_id: Session identifier
            form_id: Form identifier

        Returns:
            Updated state
        """
        state = self.get_state(session_id)

        if form_id in state["pending_forms"]:
            state["pending_forms"][form_id]["status"] = "cancelled"
            state["user_interrupt_requested"] = False

        return state

    async def get_visible_components(
        self,
        session_id: str
    ) -> list:
        """Get all visible components for session.

        Args:
            session_id: Session identifier

        Returns:
            List of visible component states
        """
        state = self.get_state(session_id)
        return [
            comp for comp in state["active_components"].values()
            if comp["visible"] and not comp["dismissed"]
        ]


def get_frontend_state_machine() -> FrontendStateMachine:
    """Get frontend state machine instance.

    Returns:
        FrontendStateMachine instance
    """
    return FrontendStateMachine()
```

### Step 2: Update langgraph __init__.py

Update file `agentx/agent/langgraph/__init__.py`:

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
from agentx.agent.langgraph.backend_state_machine import (
    BackendStateMachine,
    get_backend_state_machine,
)
from agentx.agent.langgraph.frontend_state_machine import (
    FrontendStateMachine,
    get_frontend_state_machine,
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
    "BackendStateMachine",
    "FrontendStateMachine",
    "get_backend_state_machine",
    "get_frontend_state_machine",
]
```

---

## Expected Failures & Countermeasures

### Failure: Component not found

**Likelihood**: Medium
**Symptoms**: `ValueError: Component not found`

**Countermeasures**:
1. State machine validates component exists before update
2. Returns clear error message
3. Frontend can handle error gracefully
4. Component may have been auto-dismissed

**Recovery Time**: 0 minutes (graceful error handling)

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T400 states changed
**Detection**: State field names don't match
**Action**: Update state machine to use new state fields

**Recovery Time**: 10 minutes

### Downstream Impact

**Scenario**: FrontendStateMachine method names change
**Prevention**: All method names are LOCKED
**Mitigation**: Update all use sites
**Affected Tasks**: T403 (Tests), Phase 6 (Frontend)

---

## Artifacts

**Files Created**:
- `agentx/agent/langgraph/frontend_state_machine.py` (Frontend state machine, LOCKED)

**Files Modified**:
- `agentx/agent/langgraph/__init__.py` (Add exports)

**Locked APIs**:
- FrontendStateMachine class name
- All method signatures
- State transition names

---

## Quality Gates

**Quality Checks**:
- **Check**: Frontend state machine file exists
  - Command: `test -f agentx/agent/langgraph/frontend_state_machine.py && echo "OK"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Can be imported
  - Command: `python3 -c "from agentx.agent.langgraph.frontend_state_machine import FrontendStateMachine; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. Frontend state machine manages UI lifecycle
2. Components: create → update → dismiss
3. Chat visibility: visible → minimized → hidden
4. Forms: start interrupt → submit → resume
5. Component focus for keyboard navigation
6. State stored per session (in-memory)

---

## Completion Checklist

- [ ] frontend_state_machine.py created
- [ ] FrontendStateMachine class defined
- [ ] Component lifecycle methods implemented
- [ ] Chat visibility methods implemented
- [ ] Form interrupt/resume methods implemented
- [ ] get_frontend_state_machine() factory function
- [ ] __init__.py updated
- [ ] All imports work
- [ ] Ready for T403 (Phase 4 Tests)

---

**Task T402 is part of Phase 4: LangGraph State Machines**
**Locked APIs**: FrontendStateMachine class name, method signatures
