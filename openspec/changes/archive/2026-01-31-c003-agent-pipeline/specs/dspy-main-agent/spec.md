# Spec: dspy-main-agent

**File**: `specs/dspy-main-agent/spec.md`

**Generated**: 2026-01-28
**Change**: c003-agent-pipeline

---

## 1.1 Purpose

Define the main DSPy ReAct agent that implements the conference room orchestration pattern. The MainDSPyReActAgent acts as CEO, orchestrating UI and RAG specialist agents through tool-based integration.

---

## 1.2 Scope

**In Scope**:
- MainDSPyReActAgent class with multi-signature pattern
- Tool selection and confidence scoring sub-modules
- Integration with UI and RAG specialist agents as tools
- Streaming support with dspy.streamify()
- WebSocket message generation for reasoning steps and tool calls

**Out of Scope**:
- UI specialist agent (covered by dspy-ui-agent spec)
- RAG specialist agent (covered by dspy-rag-agent spec)
- LangGraph state machine integration (covered by langgraph-state-machines spec)

---

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-MAIN-001 | Agent MUST accept user_query, conversation_history, and retrieved_context as inputs | Must |
| FR-MAIN-002 | Agent MUST return dspy.Prediction with reasoning, final_answer, confidence_score, tool_calls, and reasoning_steps | Must |
| FR-MAIN-003 | Agent MUST support optional UI callback for streaming reasoning steps | Must |
| FR-MAIN-004 | Agent MUST wrap all tools with dspy.Tool(name="...", desc="...") | Must |
| FR-MAIN-005 | Agent MUST implement synchronous warmup before async streaming | Must |
| FR-MAIN-006 | Agent MUST use dspy.ReAct with max_iters=8 by default | Should |
| FR-MAIN-007 | Agent MUST score confidence on all responses | Must |
| FR-MAIN-008 | Agent MUST extract reasoning steps from trajectory | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-MAIN-001 | Agent forward() method MUST complete within 30 seconds for typical queries | Must |
| NFR-MAIN-002 | Agent file MUST NOT exceed 120 lines (100 executable + 20 overhead) | Must |
| NFR-MAIN-003 | Agent MUST use absolute imports only | Must |
| NFR-MAIN-004 | Agent MUST pass ruff check and ruff format | Must |

---

## 1.4 Data Model

**Locked from LLD: agent_runtime.md:368-484**

```python
# File: agent/dspy_agents/main_react_agent.py
import dspy
from typing import List, Dict, Any, Optional, Callable

from agent.dspy_signatures.main_signatures import (
    MainAgentSignature,
    ToolSelectionSignature,
    ConfidenceScoringSignature
)


class MainDSPyReActAgent(dspy.Module):
    """Main agent using multi-signature ReAct pattern.

    Conference Room Pattern:
    - CEO Agent (this class) orchestrates specialists
    - UI Agent (UIDSPyAgent) handles UI generation
    - RAG Agent (RAGDSPyAgent) handles context retrieval
    """

    def __init__(
        self,
        tools: List[dspy.Tool],
        max_iters: int = 8,
        confidence_threshold: float = 0.7
    ):
        super().__init__()

        self.tools = tools
        self.max_iters = max_iters
        self.confidence_threshold = confidence_threshold

        # Sub-modules
        self.tool_selector = dspy.Predict(ToolSelectionSignature)
        self.confidence_scorer = dspy.Predict(ConfidenceScoringSignature)

        # Main ReAct loop
        self.react = dspy.ReAct(
            signature=MainAgentSignature,
            tools=tools,
            max_iters=max_iters
        )

    def forward(
        self,
        user_query: str,
        conversation_history: List[str],
        retrieved_context: str = ""
    ) -> dspy.Prediction:
        """Execute agent reasoning."""

    async def execute(
        self,
        user_query: str,
        conversation_history: List[str],
        retrieved_context: str,
        ui_callback: Optional[Callable] = None
    ) -> dspy.Prediction:
        """Execute agent with optional UI callback for streaming."""
```

**Locked from LLD: agent_runtime.md:30-56**

```python
# File: agent/dspy_signatures/main_signatures.py
import dspy
from typing import List


class MainAgentSignature(dspy.Signature):
    """Main agent reasoning signature for handling user queries."""

    user_query: str = dspy.InputField(desc="User's query or request")
    conversation_history: List[str] = dspy.InputField(desc="Conversation history (list of messages)")
    retrieved_context: str = dspy.InputField(desc="Retrieved context from RAG")
    reasoning: str = dspy.OutputField(desc="Step-by-step reasoning process")
    final_answer: str = dspy.OutputField(desc="Final response to user")


class ToolSelectionSignature(dspy.Signature):
    """Select appropriate tools based on query analysis."""

    query_analysis: str = dspy.InputField(desc="Analysis of user query")
    available_tools: List[str] = dspy.InputField(desc="List of available tool names")
    selected_tools: List[str] = dspy.OutputField(desc="Tools to use for this query")
    tool_rationale: str = dspy.OutputField(desc="Reasoning for tool selection")


class ConfidenceScoringSignature(dspy.Signature):
    """Score confidence in the generated response."""

    response: str = dspy.InputField(desc="Generated response")
    context_quality: str = dspy.InputField(desc="Quality of retrieved context")
    confidence_score: float = dspy.OutputField(desc="Confidence from 0.0 to 1.0")
    confidence_reasoning: str = dspy.OutputField(desc="Explanation of confidence score")
```

---

## 1.5 API Contract

### REST Endpoints

| Method | Path | Request | Response | Status Codes |
|--------|------|---------|----------|--------------|
| POST | `/api/v1/agent/query` | `ExecuteAgentQueryCommand` | `ExecuteAgentQueryResponse` | 200, 400, 500 |
| POST | `/api/v1/agent/stream` | `ExecuteAgentQueryCommand` | Server-Sent Events | 200, 400, 500 |

**ExecuteAgentQueryCommand**:
```python
class ExecuteAgentQueryCommand(BaseModel):
    session_id: UUID
    query: str = Field(..., min_length=1)
    stream: bool = Field(default=False)
```

**ExecuteAgentQueryResponse**:
```python
class ExecuteAgentQueryResponse(BaseModel):
    session_id: UUID
    answer: str
    confidence_score: float
    reasoning_steps: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    ui_descriptors: List[Dict[str, Any]] = Field(default_factory=list)
```

### WebSocket Channels

| Channel | Direction | Message Schema |
|---------|-----------|----------------|
| `/ws/agent/{session_id}` | Bidirectional | TOKEN, REASONING_STEP, TOOL_CALL, DESCRIPTOR_* |

**WebSocket Message Types**:
```python
# From C002 data contracts
class WebSocketMessageType(str, Enum):
    TOKEN = "token"
    REASONING_STEP = "reasoning_step"
    TOOL_CALL = "tool_call"
    DESCRIPTOR_CREATE = "descriptor_create"
    DESCRIPTOR_UPDATE = "descriptor_update"
    DESCRIPTOR_DISMISS = "descriptor_dismiss"
```

---

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| **BR-MAIN-001** | Tool selection MUST use query analysis, not random selection | Code in tool_selector |
| **BR-MAIN-002** | Confidence score below threshold MUST trigger fallback or clarification | Code in execute() |
| **BR-MAIN-003** | Max iterations MUST NOT exceed 8 to prevent infinite loops | Configuration in __init__ |
| **BR-MAIN-004** | All tools MUST be wrapped with dspy.Tool() | Code review + tests |
| **BR-MAIN-005** | Synchronous warmup MUST be called before async streaming | Code in execute() |

---

## 1.7 Acceptance Criteria

- [ ] MainDSPyReActAgent compiles without errors
- [ ] All tools wrapped with dspy.Tool(func, name="...", desc="...")
- [ ] Sync warmup pattern implemented before async operations
- [ ] Returns all required prediction fields (reasoning, final_answer, confidence_score, tool_calls, reasoning_steps)
- [ ] File under 120 lines (100 executable + 20 overhead)
- [ ] Integration test passes with calculator tool
- [ ] WebSocket test receives REASONING_STEP and TOOL_CALL messages
- [ ] Confidence scoring returns value between 0.0 and 1.0
- [ ] Max iterations enforced (stops after 8 steps)

---

**Related Specs**:
- `specs/dspy-ui-agent/spec.md` - UI specialist agent
- `specs/dspy-rag-agent/spec.md` - RAG specialist agent
- `specs/langgraph-state-machines/spec.md` - State machine integration
