# T401: Create Backend State Machine

**Phase**: 4
**Estimated Time**: 45 minutes
**Dependencies**: T001, T400, T202
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/agent_runtime.md` - Backend LangGraph state machine
- `lld/incremental_release_plan.md` - Phase 4: Backend state machine

**Description**:
Creates LangGraph state machine for backend agent execution. Handles agent lifecycle: idle → reasoning → tool use → completed.

---

## Acceptance Criteria

**Passing Criteria**:
- agent/langgraph/backend_state_machine.py exists
- LangGraph graph defined with nodes and edges
- State transitions implemented (idle → reasoning → completed)
- Can be imported and instantiated
- Has run() method for execution

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/agent/langgraph/backend_state_machine.py && echo "Backend state machine exists"

# Verify import works
python3 -c "from agentx.agent.langgraph.backend_state_machine import BackendStateMachine; print('Import OK')"
```

---

## Implementation Steps

### Step 1: Create backend state machine

Create file `agentx/agent/langgraph/backend_state_machine.py`:

```python
"""Backend LangGraph state machine for agent execution."""

import asyncio
from typing import Dict, Any, Literal
from datetime import datetime
from uuid import uuid4

from agentx.agent.langgraph.states import (
    BackendLangGraphState,
    AgentStatus,
    ReasoningStep,
    ToolCall,
)


class BackendStateMachine:
    """LangGraph state machine for backend agent execution.

    This state machine manages the agent lifecycle:
    1. Initialize state
    2. Run reasoning
    3. Execute tools
    4. Generate final answer
    5. Handle errors

    Example:
        >>> machine = BackendStateMachine()
        >>> result = await machine.run(session_id="test", user_query="What is 2+2?")
    """

    def __init__(self):
        """Initialize state machine."""
        from agentx.agent.dspy_agents import get_main_agent
        self.agent = get_main_agent()

    async def run(
        self,
        session_id: str,
        user_query: str,
        conversation_history: list = None,
        retrieved_context: str = ""
    ) -> BackendLangGraphState:
        """Run agent through state machine.

        Args:
            session_id: Session identifier
            user_query: User's query
            conversation_history: Previous conversation turns
            retrieved_context: Retrieved context from RAG/memory

        Returns:
            Final state after execution
        """
        # Initialize state
        state: BackendLangGraphState = {
            "session_id": session_id,
            "user_query": user_query,
            "conversation_history": conversation_history or [],
            "retrieved_context": retrieved_context,
            "reasoning_steps": [],
            "current_step": 0,
            "tool_calls": [],
            "agent_status": AgentStatus.IDLE,
            "confidence_score": 0.0,
            "should_continue": True,
            "final_answer": None,
            "error_message": None,
        }

        try:
            # Transition to thinking
            state = await self._transition_to_thinking(state)

            # Execute agent
            state = await self._execute_agent(state)

            # Complete
            state = await self._transition_to_completed(state)

        except Exception as e:
            # Handle error
            state = await self._transition_to_failed(state, str(e))

        return state

    async def _transition_to_thinking(
        self,
        state: BackendLangGraphState
    ) -> BackendLangGraphState:
        """Transition to thinking state.

        Args:
            state: Current state

        Returns:
            Updated state
        """
        state["agent_status"] = AgentStatus.THINKING
        state["current_step"] = 1
        return state

    async def _execute_agent(
        self,
        state: BackendLangGraphState
    ) -> BackendLangGraphState:
        """Execute agent reasoning.

        Args:
            state: Current state

        Returns:
            Updated state with results
        """
        # Build conversation history string
        history_str = self._format_conversation_history(state["conversation_history"])

        # Run DSPy agent
        prediction = self.agent(
            user_query=state["user_query"],
            conversation_history=history_str,
            retrieved_context=state["retrieved_context"]
        )

        # Extract reasoning steps
        state["reasoning_steps"] = self._extract_reasoning_steps(prediction)
        state["current_step"] = len(state["reasoning_steps"])

        # Extract tool calls
        state["tool_calls"] = self._extract_tool_calls(prediction)

        # Store final answer
        state["final_answer"] = getattr(prediction, "final_answer", "")
        state["confidence_score"] = float(getattr(prediction, "confidence_score", 0.0))

        return state

    async def _transition_to_completed(
        self,
        state: BackendLangGraphState
    ) -> BackendLangGraphState:
        """Transition to completed state.

        Args:
            state: Current state

        Returns:
            Updated state
        """
        state["agent_status"] = AgentStatus.COMPLETED
        state["should_continue"] = False
        return state

    async def _transition_to_failed(
        self,
        state: BackendLangGraphState,
        error_message: str
    ) -> BackendLangGraphState:
        """Transition to failed state.

        Args:
            state: Current state
            error_message: Error message

        Returns:
            Updated state
        """
        state["agent_status"] = AgentStatus.FAILED
        state["error_message"] = error_message
        state["should_continue"] = False
        return state

    def _format_conversation_history(self, history: list) -> str:
        """Format conversation history for DSPy.

        Args:
            history: List of conversation turns

        Returns:
            Formatted history string
        """
        if not history:
            return ""

        formatted = []
        for turn in history[-5:]:  # Last 5 turns
            role = turn.get("role", "user")
            content = turn.get("content", "")
            formatted.append(f"{role}: {content}")

        return "\\n".join(formatted)

    def _extract_reasoning_steps(self, prediction) -> list:
        """Extract reasoning steps from prediction.

        Args:
            prediction: DSPy prediction

        Returns:
            List of reasoning steps
        """
        reasoning = getattr(prediction, "reasoning", "")
        if not reasoning:
            return []

        steps = []
        lines = reasoning.split("\\n")
        for i, line in enumerate(lines, 1):
            if line.strip():
                steps.append(ReasoningStep(
                    step_number=i,
                    thought=line.strip(),
                    action=None,
                    observation=None,
                    timestamp=datetime.utcnow().isoformat()
                ))

        return steps

    def _extract_tool_calls(self, prediction) -> list:
        """Extract tool calls from prediction.

        Args:
            prediction: DSPy prediction

        Returns:
            List of tool calls
        """
        trajectory = getattr(prediction, "tool_calls", [])
        if not trajectory:
            return []

        calls = []
        for call in trajectory:
            calls.append(ToolCall(
                tool_name=getattr(call, "tool", "unknown"),
                arguments=getattr(call, "args", {}),
                result=getattr(call, "result", None),
                error=getattr(call, "error", None),
                duration_ms=0,  # Not tracked in Phase 2
                timestamp=datetime.utcnow().isoformat()
            ))

        return calls


def get_backend_state_machine() -> BackendStateMachine:
    """Get backend state machine instance.

    Returns:
        BackendStateMachine instance
    """
    return BackendStateMachine()
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
    "get_backend_state_machine",
]
```

---

## Expected Failures & Countermeasures

### Failure: State machine execution fails

**Likelihood**: Medium
**Symptoms**: Exception during agent execution

**Countermeasures**:
1. State machine catches exceptions and transitions to FAILED
2. Error message stored in state
3. Frontend can display error to user
4. Agent can be re-run after failure

**Recovery Time**: 0 minutes (graceful error handling)

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T202 agent changed
**Detection**: Agent method signatures changed
**Action**: Update _execute_agent to use new agent interface

**Recovery Time**: 10 minutes

**Scenario**: T400 states changed
**Detection**: State field names don't match
**Action**: Update state machine to use new state fields

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: BackendStateMachine class name changes
**Prevention**: Class name is LOCKED
**Mitigation**: Update all use sites
**Affected Tasks**: T402 (Frontend State Machine), T403 (Tests)

---

## Artifacts

**Files Created**:
- `agentx/agent/langgraph/backend_state_machine.py` (Backend state machine, LOCKED)

**Files Modified**:
- `agentx/agent/langgraph/__init__.py` (Add exports)

**Locked APIs**:
- BackendStateMachine class name
- All method signatures
- State transition names

---

## Quality Gates

**Quality Checks**:
- **Check**: Backend state machine file exists
  - Command: `test -f agentx/agent/langgraph/backend_state_machine.py && echo "OK"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Can be imported
  - Command: `python3 -c "from agentx.agent.langgraph.backend_state_machine import BackendStateMachine; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. State machine manages agent lifecycle
2. States: IDLE → THINKING → USING_TOOL → COMPLETED/FAILED
3. All exceptions caught and transition to FAILED
4. Reasoning steps extracted for frontend streaming
5. Tool calls tracked with timestamps
6. Conversation history limited to last 5 turns

---

## Completion Checklist

- [ ] backend_state_machine.py created
- [ ] BackendStateMachine class defined
- [ ] run() method implements full lifecycle
- [ ] State transition methods implemented
- [ ] Error handling with FAILED state
- [ ] get_backend_state_machine() factory function
- [ ] __init__.py updated
- [ ] All imports work
- [ ] Ready for T402 (Frontend State Machine)

---

**Task T401 is part of Phase 4: LangGraph State Machines**
**Locked APIs**: BackendStateMachine class name, method signatures
