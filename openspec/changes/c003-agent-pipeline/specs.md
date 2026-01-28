# Specs Artifact: c003-agent-pipeline

**Generated**: 2026-01-28
**Change**: c003-agent-pipeline
**Schema**: spec-factory v1

---

## Spec Structure

This artifact generates domain-specific specification files in `specs/{domain}/spec.md`.

---

## 1. Spec: dspy-main-agent

**File**: `specs/dspy-main-agent/spec.md`

### 1.1 Purpose

Define the main DSPy ReAct agent that implements the conference room orchestration pattern. The MainDSPyReActAgent acts as CEO, orchestrating UI and RAG specialist agents through tool-based integration.

### 1.2 Key Requirements

- **FR-MAIN-001**: Agent MUST accept user_query, conversation_history, and retrieved_context as inputs
- **FR-MAIN-002**: Agent MUST return dspy.Prediction with reasoning, final_answer, confidence_score, tool_calls, reasoning_steps
- **FR-MAIN-004**: Agent MUST wrap all tools with dspy.Tool(name="...", desc="...")
- **FR-MAIN-005**: Agent MUST implement synchronous warmup before async streaming

### 1.3 Locked from LLD

```python
# agent_runtime.md:368-484
class MainDSPyReActAgent(dspy.Module):
    def __init__(self, tools: List[dspy.Tool], max_iters: int = 8, confidence_threshold: float = 0.7)
    def forward(self, user_query: str, conversation_history: List[str], retrieved_context: str) -> dspy.Prediction
    async def execute(self, user_query: str, conversation_history: List[str], retrieved_context: str, ui_callback: Optional[Callable] = None) -> dspy.Prediction
```

### 1.4 API Contract

| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/api/v1/agent/query` | `ExecuteAgentQueryCommand` | `ExecuteAgentQueryResponse` |
| POST | `/api/v1/agent/stream` | `ExecuteAgentQueryCommand` | Server-Sent Events |

---

## 2. Spec: dspy-ui-agent

**File**: `specs/dspy-ui-agent/spec.md`

### 2.1 Purpose

Define the UI specialist agent that generates UI descriptors for displaying content to users. The UIDSPyAgent is responsible for selecting appropriate widgets, configuring forms, generating cards and confirmations, and updating progress indicators.

### 2.2 Key Requirements

- **FR-UI-001**: Agent MUST select widget type based on content_type and context
- **FR-UI-006**: Agent MUST return descriptor IDs (not full descriptor objects)
- **FR-UI-007**: Agent MUST NOT generate HTML or CSS directly

### 2.3 Locked from LLD

```python
# agent_runtime.md:486-580
class UIDSPyAgent(dspy.Module):
    def select_widget(self, content_type: str, context: str) -> dspy.Prediction
    def configure_form(self, required_fields: List[str], context: str) -> dspy.Prediction
    def show_card(self, title: str, content: str, context: str) -> dspy.Prediction
    def request_confirmation(self, action_description: str, risk_level: str) -> dspy.Prediction
    def update_progress(self, task_name: str, current_step: int, total_steps: int) -> dspy.Prediction
```

### 2.4 Descriptor ID Format

All UI tools return descriptor IDs in the format:
```
{DESCRIPTOR_TYPE}:{uuid}
```

Examples: `MARKDOWN_BLOCK:550e8400-e29b-41d4-a716-446655440000`

---

## 3. Spec: dspy-rag-agent

**File**: `specs/dspy-rag-agent/spec.md`

### 3.1 Purpose

Define the RAG specialist agent that implements agentic retrieval-augmented generation. The RAGDSPyAgent is responsible for retrieving relevant memories, scoring context quality, deciding whether to inject context, and filtering/formatting context for the main agent.

### 3.2 Key Requirements

- **FR-RAG-002**: Agent MUST limit retrieved memories to 10 items
- **FR-RAG-003**: Agent MUST score context quality (high/low) based on relevance
- **FR-RAG-004**: Agent MUST decide whether to inject context based on query relevance
- **FR-RAG-006**: Agent MUST implement agentic RAG (not simple context dump)

### 3.3 Locked from LLD

```python
# agent_runtime.md:582-663
class RAGDSPyAgent(dspy.Module):
    def retrieve_context(self, query: str, user_id: str, limit: int = 10) -> dspy.Prediction
    def should_inject_context(self, query: str, retrieved_context: str) -> dspy.Prediction
```

### 3.4 Agentic RAG Flow

```
User Query → RAGDSPyAgent.retrieve_context() → Search Memories → Format Results
    → RAGDSPyAgent.should_inject_context() → DSPy Decide → Filter & Format
    → MainDSPyReActAgent (with context)
```

---

## 4. Spec: langgraph-state-machines

**File**: `specs/langgraph-state-machines/spec.md`

### 4.1 Purpose

Define LangGraph state machines for backend agent reasoning flow and frontend UI component lifecycle. State machines provide declarative, visualizable control flow with built-in state management and error handling.

### 4.2 Key Requirements

- **FR-LG-001**: Backend state machine MUST transition through IDLE → THINKING → USING_TOOL → COMPLETED
- **FR-LG-002**: Frontend state machine MUST support create, update, dismiss, form_submit, progress operations
- **FR-LG-003**: State machines MUST use TypedDict for state schemas
- **FR-LG-006**: Form interrupt MUST pause agent execution until form submitted

### 4.3 Locked from LLD

```python
# agent_runtime.md:681-750
class BackendLangGraphState(TypedDict):
    session_id: str
    user_query: str
    conversation_history: List[Dict[str, str]]
    retrieved_context: str
    reasoning_steps: List[Dict[str, Any]]
    current_step: int
    agent_status: AgentStatus
    confidence_score: float
    should_continue: bool
    error_message: str

# agent_runtime.md:764-773
class FrontendLangGraphState(TypedDict):
    session_id: str
    active_components: Dict[str, Dict[str, Any]]
    visibility_state: VisibilityState
    focused_component_id: str
    pending_forms: Dict[str, Dict[str, Any]]
    stream_queue: List[Dict[str, Any]]
    form_interrupt: bool
```

### 4.4 State Transition Table (Backend)

| Current State | Event | Next State | Action |
|---------------|-------|------------|--------|
| IDLE | query_received | THINKING | Set agent_status=THINKING |
| THINKING | step_complete | USING_TOOL | Execute tool, increment step |
| USING_TOOL | tool_complete | THINKING | Check completion condition |
| THINKING | should_continue=False | COMPLETED | Set should_continue=False |
| USING_TOOL | error | FAILED | Set error_message |

---

## 5. Cross-Domain Contracts

### 5.1 Shared Types

**AgentStatus Enum** (used by BackendLangGraphState):
```python
class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    USING_TOOL = "using_tool"
    COMPLETED = "completed"
    FAILED = "failed"
```

**SessionState Enum** (used by AgentSessionEntity):
```python
class SessionState(str, Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
```

### 5.2 Integration Points

| Domain A | Domain B | Interface |
|----------|----------|-----------|
| **dspy-main-agent** | **dspy-ui-agent** | UIDSPyAgent exposed as tool via dspy.Tool() |
| **dspy-main-agent** | **dspy-rag-agent** | RAGDSPyAgent called before main agent for context retrieval |
| **dspy-main-agent** | **langgraph-state-machines** | MainDSPyReActAgent.execute() called from backend state machine node |
| **langgraph-state-machines** | **C002-data-contracts** | State changes trigger WebSocket messages (DESCRIPTOR_CREATE, etc.) |

### 5.3 Data Flow

```
User Query
    ↓
ExecuteAgentQueryUseCase
    ↓
RAGDSPyAgent.retrieve_context() → Qdrant/Mem0AI
    ↓
RAGDSPyAgent.should_inject_context() → Filter decision
    ↓
BackendLangGraphState (initial)
    ↓
start_reasoning node → IDLE → THINKING
    ↓
execute_step node → MainDSPyReActAgent.forward()
    ├─→ UIDSPyAgent (via tool) → UI descriptor ID
    └─→ ConfidenceScoringSignature → confidence_score
    ↓
check_completion node → COMPLETED
    ↓
FrontendLangGraphState → WebSocket messages
```

---

## 6. Pydantic → Zod Type Mappings

### 6.1 Shared DTOs

**Backend (Pydantic v2)**:
```python
class ExecuteAgentQueryCommand(BaseModel):
    session_id: UUID
    query: str = Field(..., min_length=1)
    stream: bool = Field(default=False)

class ExecuteAgentQueryResponse(BaseModel):
    session_id: UUID
    answer: str
    confidence_score: float
    reasoning_steps: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    ui_descriptors: List[Dict[str, Any]] = Field(default_factory=list)

class ReasoningStep(BaseModel):
    step_number: int
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None

class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[str] = None
    error: Optional[str] = None
    duration_ms: int
```

**Frontend (Zod)**:
```typescript
export const ExecuteAgentQueryCommandSchema = z.object({
  session_id: z.string().uuid(),
  query: z.string().min(1),
  stream: z.boolean().default(false),
});

export const ExecuteAgentQueryResponseSchema = z.object({
  session_id: z.string().uuid(),
  answer: z.string(),
  confidence_score: z.number(),
  reasoning_steps: z.array(
    z.object({
      step_number: z.number(),
      thought: z.string(),
      action: z.string().optional(),
      observation: z.string().optional(),
    })
  ),
  tool_calls: z.array(
    z.object({
      tool_name: z.string(),
      arguments: z.record(z.any()),
      result: z.string().optional(),
      error: z.string().optional(),
      duration_ms: z.number(),
    })
  ),
  ui_descriptors: z.array(z.any()).default([]),
});
```

### 6.2 Type Mapping Table

| Pydantic v2 Type | Zod Type | Notes |
|------------------|----------|-------|
| `str` | `z.string()` | Direct mapping |
| `str \| None` | `z.string().optional()` | Use optional() |
| `int` | `z.number()` | Zod has no int type |
| `float` | `z.number()` | Direct mapping |
| `bool` | `z.boolean()` | Direct mapping |
| `datetime` | `z.string().datetime()` | Format as ISO string |
| `UUID` | `z.string().uuid()` | Format as UUID string |
| `List[str]` | `z.array(z.string())` | Array of strings |
| `Dict[str, Any]` | `z.record(z.any())` | Key-value record |
| `Literal["a", "b"]` | `z.enum(["a", "b"])` | Closed set enum |
| `AgentStatus` (Enum) | `z.enum(["idle", "thinking", ...])` | Match enum values |

---

**Next Artifact**: design.md
