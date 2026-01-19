# T203: Create Agent Use Cases

**Phase**: 2
**Estimated Time**: 35 minutes
**Dependencies**: T001, T202, T100
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/application_services.md` - Use case definitions
- `lld/incremental_release_plan.md` - Phase 2: ExecuteAgentQuery use case

**Description**:
Creates application use case for executing agent queries. Use cases orchestrate domain logic and provide clean API boundaries.

---

## Acceptance Criteria

**Passing Criteria**:
- ExecuteAgentQueryUseCase exists
- Has execute() method
- Uses MainDSPyReActAgent
- Returns DTOs
- Can be imported

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify use case file exists
test -f agentx/application/use_cases/execute_agent_query_use_case.py && echo "Use case exists"

# Verify import works
python3 -c "from agentx.application.use_cases.execute_agent_query_use_case import ExecuteAgentQueryUseCase; print('Import OK')"
```

---

## Implementation Steps

### Step 1: Create DTOs

Create file `agentx/application/dtos/agent_dtos.py`:

```python
"""Data Transfer Objects for agent operations."""

from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ExecuteAgentQueryCommand(BaseModel):
    """Command to execute agent query."""

    session_id: UUID = Field(..., description="Session identifier")
    user_query: str = Field(..., description="User's query or request")
    retrieved_context: str = Field(default="", description="Retrieved context")


class ToolCallDTO(BaseModel):
    """DTO for tool execution details."""

    tool_name: str = Field(..., description="Name of tool used")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    result: Optional[str] = Field(None, description="Tool result")
    duration_ms: int = Field(..., description="Execution time in milliseconds")


class ReasoningStepDTO(BaseModel):
    """DTO for reasoning step."""

    step_number: int = Field(..., description="Step number")
    thought: str = Field(..., description="Agent's thought")
    action: Optional[str] = Field(None, description="Action taken")
    observation: Optional[str] = Field(None, description="Result observation")


class ExecuteAgentQueryResponse(BaseModel):
    """Response from agent query execution."""

    session_id: UUID = Field(..., description="Session identifier")
    reasoning: str = Field(..., description="Full reasoning process")
    final_answer: str = Field(..., description="Final answer to user")
    confidence_score: float = Field(..., description="Confidence from 0.0 to 1.0", ge=0.0, le=1.0)
    confidence_reasoning: str = Field(..., description="Explanation of confidence")
    tool_calls: List[ToolCallDTO] = Field(default_factory=list, description="Tools used")
    reasoning_steps: List[ReasoningStepDTO] = Field(default_factory=list, description="Reasoning breakdown")
```

### Step 2: Create execute agent query use case

Create file `agentx/application/use_cases/execute_agent_query_use_case.py`:

```python
"""Use case for executing agent queries."""

import time
from typing import List
from uuid import UUID

from agentx.agent.dspy_agents import get_main_agent, MainDSPyReActAgent
from agentx.application.dtos.agent_dtos import (
    ExecuteAgentQueryCommand,
    ExecuteAgentQueryResponse,
    ToolCallDTO,
    ReasoningStepDTO,
)


class ExecuteAgentQueryUseCase:
    """Use case for executing queries through the main agent.

    This use case orchestrates the agent execution flow:
    1. Validate command
    2. Get agent instance
    3. Execute query through agent
    4. Transform result to DTOs
    5. Return response

    Example:
        >>> use_case = ExecuteAgentQueryUseCase()
        >>> command = ExecuteAgentQueryCommand(
        ...     session_id=uuid4(),
        ...     user_query="What is 2+2?"
        ... )
        >>> response = await use_case.execute(command)
        >>> assert response.final_answer
    """

    def __init__(self, agent: MainDSPyReActAgent = None):
        """Initialize use case.

        Args:
            agent: Agent instance (uses singleton if not provided)
        """
        self.agent = agent or get_main_agent()

    async def execute(
        self,
        command: ExecuteAgentQueryCommand
    ) -> ExecuteAgentQueryResponse:
        """Execute agent query.

        Args:
            command: Query execution command

        Returns:
            Agent response with reasoning, answer, and metadata

        Raises:
            ValueError: If command validation fails
        """
        # Validate command
        self._validate_command(command)

        # Build conversation history (empty for Phase 2)
        conversation_history = ""

        # Execute query through agent
        start_time = time.time()
        prediction = self.agent(
            user_query=command.user_query,
            conversation_history=conversation_history,
            retrieved_context=command.retrieved_context
        )
        duration_ms = int((time.time() - start_time) * 1000)

        # Transform prediction to response
        return self._build_response(command, prediction, duration_ms)

    def _validate_command(self, command: ExecuteAgentQueryCommand) -> None:
        """Validate command parameters.

        Args:
            command: Command to validate

        Raises:
            ValueError: If validation fails
        """
        if not command.user_query or not command.user_query.strip():
            raise ValueError("user_query cannot be empty")
        if not command.session_id:
            raise ValueError("session_id is required")

    def _build_response(
        self,
        command: ExecuteAgentQueryCommand,
        prediction,
        duration_ms: int
    ) -> ExecuteAgentQueryResponse:
        """Build response DTO from prediction.

        Args:
            command: Original command
            prediction: DSPy prediction
            duration_ms: Execution time

        Returns:
            Formatted response DTO
        """
        reasoning_steps = self._extract_reasoning_steps(prediction)
        tool_calls = self._extract_tool_calls(prediction)

        return ExecuteAgentQueryResponse(
            session_id=command.session_id,
            reasoning=getattr(prediction, "reasoning", ""),
            final_answer=getattr(prediction, "final_answer", ""),
            confidence_score=float(getattr(prediction, "confidence_score", 0.0)),
            confidence_reasoning=getattr(prediction, "confidence_reasoning", ""),
            tool_calls=tool_calls,
            reasoning_steps=reasoning_steps,
        )

    def _extract_reasoning_steps(self, prediction) -> List[ReasoningStepDTO]:
        """Extract reasoning steps from prediction.

        Args:
            prediction: DSPy prediction

        Returns:
            List of reasoning step DTOs
        """
        reasoning = getattr(prediction, "reasoning", "")
        if not reasoning:
            return []

        # Split reasoning into steps (naive implementation)
        # Phase 3+ will parse structured reasoning
        steps = []
        lines = reasoning.split("\\n")
        for i, line in enumerate(lines, 1):
            if line.strip():
                steps.append(ReasoningStepDTO(
                    step_number=i,
                    thought=line.strip(),
                    action=None,
                    observation=None
                ))

        return steps

    def _extract_tool_calls(self, prediction) -> List[ToolCallDTO]:
        """Extract tool calls from prediction.

        Args:
            prediction: DSPy prediction

        Returns:
            List of tool call DTOs
        """
        trajectory = getattr(prediction, "tool_calls", [])
        if not trajectory:
            return []

        tool_calls = []
        for call in trajectory:
            tool_calls.append(ToolCallDTO(
                tool_name=getattr(call, "tool", "unknown"),
                arguments=getattr(call, "args", {}),
                result=getattr(call, "result", None),
                duration_ms=0  # Not tracked in Phase 2
            ))

        return tool_calls
```

### Step 3: Update application layer __init__.py files

Create file `agentx/application/dtos/__init__.py`:

```python
"""Application DTOs."""

from agentx.application.dtos.agent_dtos import (
    ExecuteAgentQueryCommand,
    ExecuteAgentQueryResponse,
    ToolCallDTO,
    ReasoningStepDTO,
)

__all__ = [
    "ExecuteAgentQueryCommand",
    "ExecuteAgentQueryResponse",
    "ToolCallDTO",
    "ReasoningStepDTO",
]
```

Create file `agentx/application/use_cases/__init__.py`:

```python
"""Application use cases."""

from agentx.application.use_cases.execute_agent_query_use_case import (
    ExecuteAgentQueryUseCase,
)

__all__ = [
    "ExecuteAgentQueryUseCase",
]
```

---

## Expected Failures & Countermeasures

### Failure: Agent not initialized

**Likelihood**: Medium
**Symptoms**: `AttributeError: 'NoneType' object has no attribute 'forward'`

**Countermeasures**:
1. Ensure T202 (Main DSPy Agent) is complete
2. Check Ollama is running: `ollama serve`
3. Verify agent factory creates instance
4. Check get_main_agent() returns valid instance

**Recovery Time**: 5 minutes

### Failure: Pydantic validation error

**Likelihood**: Low
**Symptoms**: `pydantic.ValidationError` on DTO creation

**Countermeasures**:
1. Check DTO field types match prediction attributes
2. Ensure all required fields have values
3. Add default values for optional fields
4. Validate confidence_score is float between 0.0 and 1.0

**Recovery Time**: 5 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T202 agent changed
**Detection**: Agent method signatures changed
**Action**: Update use case to match new agent interface

**Recovery Time**: 10 minutes

**Scenario**: T100 entities changed
**Detection**: DTO field types don't match
**Action**: Update DTOs to match entity structure

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Use case class name changes
**Prevention**: ExecuteAgentQueryUseCase class name is LOCKED
**Mitigation**: Update API routes and tests
**Affected Tasks**: T204 (Tests), Phase 3 (API Routes)

---

## Artifacts

**Files Created**:
- `agentx/application/dtos/agent_dtos.py` (DTOs, LOCKED)
- `agentx/application/use_cases/execute_agent_query_use_case.py` (Use case, LOCKED)
- `agentx/application/dtos/__init__.py` (Package marker)
- `agentx/application/use_cases/__init__.py` (Package marker)

**Locked APIs**:
- `ExecuteAgentQueryUseCase` class name
- `execute()` method signature
- All DTO class names
- All DTO field names and types

---

## Quality Gates

**Quality Checks**:
- **Check**: Use case file exists
  - Command: `test -f agentx/application/use_cases/execute_agent_query_use_case.py && echo "OK"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Use case can be imported
  - Command: `python3 -c "from agentx.application.use_cases.execute_agent_query_use_case import ExecuteAgentQueryUseCase; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Use case can be instantiated
  - Command: `python3 -c "from agentx.application.use_cases.execute_agent_query_use_case import ExecuteAgentQueryUseCase; uc = ExecuteAgentQueryUseCase(); print(type(uc).__name__)"`
  - Expected: `ExecuteAgentQueryUseCase`
  - Required: Yes

---

## Notes

1. Use case pattern: Single-purpose class with execute() method
2. DTOs separate from entities (Clean Architecture)
3. Async interface for future WebSocket integration
4. Command validation in use case (not in DTO)
5. Transform prediction to response DTO

---

## Completion Checklist

- [ ] agent_dtos.py created with all DTOs
- [ ] execute_agent_query_use_case.py created
- [ ] ExecuteAgentQueryUseCase implements execute() method
- [ ] DTOs exported in __init__.py
- [ ] Use case exported in __init__.py
- [ ] All imports work
- [ ] Ready for T204 (Phase 2 Tests)

---

**Task T203 is part of Phase 2: Main DSPy Agent**
**Locked APIs**: Use case class name, DTO definitions
