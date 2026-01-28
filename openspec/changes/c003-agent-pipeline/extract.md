# Extract Artifact: c003-agent-pipeline

**Generated**: 2026-01-28
**Change**: c003-agent-pipeline
**Schema**: spec-factory v1

---

## 1. Pattern Catalog

### 1.1 Architectural Patterns

| Pattern | Source | Description | Apply? |
|---------|--------|-------------|--------|
| **Clean Architecture** | mimicus | Layered separation: domain/, infrastructure/, agent/, application/, presentation/ | ✅ |
| **Repository Pattern** | mimicus | ABC base class + implementations (Redis, Qdrant, Mem0AI) | ✅ |
| **DTO Pattern** | mimicus | Pydantic models for API layer (Command/Response separation) | ✅ |
| **Conference Room Pattern** | R014 | CEO agent (MainDSPyReActAgent) orchestrates UI and RAG specialists | ✅ |
| **LangGraph State Machines** | LLD agent_runtime.md | Backend state (agent reasoning) + Frontend state (UI lifecycle) | ✅ |
| **Agentic RAG** | Research + LLD | Retrieve → Score → Decide → Filter (not simple context dump) | ✅ |
| **Three-Tier Memory** | LLD incremental_release_plan.md | Tier 1 (session), Tier 2 (Qdrant), Tier 3 (Mem0AI + consolidation) | ✅ |
| **Use Case Pattern** | mimicus | Single-purpose classes with `execute()` method | ✅ |
| **Dependency Injection** | mimicus | Global singletons + getter functions in `core/dependencies.py` | ✅ |

### 1.2 Code Structure Patterns

| Pattern | Example | Apply? |
|---------|---------|--------|
| **@dataclass entities** | `class AgentSessionEntity:` with business methods | ✅ |
| **ABC repositories** | `class AgentSessionRepository(ABC):` with abstract methods | ✅ |
| **Static mappers** | `@staticmethod def to_dto()`, `@staticmethod def to_entity()` | ✅ |
| **Use case classes** | `class ExecuteAgentQueryUseCase:` with `execute()` | ✅ |
| **DSPy Module pattern** | `class MainDSPyReActAgent(dspy.Module):` with `forward()` | ✅ |
| **Tool wrapping** | `dspy.Tool(func, name="...", desc="...")` - prevents hallucination | ✅ |
| **Streaming pattern** | `dspy.streamify()` with `StreamListener(allow_reuse=True)` | ✅ |
| **Sync warmup** | Required: Call module synchronously before async streaming | ✅ |
| **File size limit** | Max 100 lines executable + 50 lines overhead | ✅ |

### 1.3 Naming Patterns (to Avoid from R014)

| R014 Name | Why Avoid | Alternative |
|-----------|-----------|-------------|
| `IntelligentUIGenerator` | Too generic, doesn't convey architecture | `UIDSPyAgent` (specialist) |
| `EnhancedExecutorAgent` | Vague "enhanced" prefix | `ContentDSPyAgent` or domain-specific name |
| `master_agent.py` | "master" has connotations; use orchestrator | `agent_orchestrator.py` or `ceo_agent.py` |
| `pipeline/` folder | Implies sequential data flow | `specialists/` or `agents/` |
| `multihop_reader.py` | "multihop" is implementation detail | `RetrievalDSPyAgent` (domain-focused) |

### 1.4 File Structure Pattern (from C001)

```
agentx/
├── agent/
│   ├── dspy_signatures/
│   │   ├── main_signatures.py      # MainAgentSignature, ToolSelectionSignature, ConfidenceScoringSignature
│   │   ├── ui_signatures.py        # SelectWidgetSignature, ConfigureFormSignature, etc.
│   │   └── rag_signatures.py       # RetrievalSignature, ContextInjectionSignature
│   ├── tools/
│   │   ├── main_tools.py           # safe_calculator, searxng_search, get_current_weather
│   │   └── ui_tools.py             # render_markdown_block, render_card, request_confirmation, update_progress
│   ├── dspy_agents/
│   │   ├── main_react_agent.py     # MainDSPyReActAgent (CEO orchestrator)
│   │   ├── ui_agent.py             # UIDSPyAgent (UI specialist)
│   │   └── rag_agent.py            # RAGDSPyAgent (RAG specialist)
│   └── langgraph/
│       ├── backend_state_machine.py    # BackendLangGraphState, workflow nodes
│       └── frontend_state_machine.py   # FrontendLangGraphState, workflow nodes
├── application/
│   ├── use_cases/
│   │   ├── execute_agent_query.py  # ExecuteAgentQueryUseCase
│   │   └── stream_ui_update.py     # StreamUIUpdateUseCase
│   ├── services/
│   │   ├── agent_orchestrator.py   # Coordinates state machines + agents
│   │   └── memory_service.py       # Memory consolidation service
│   └── dtos/
│       ├── agent_dtos.py           # ExecuteAgentQueryCommand, ExecuteAgentQueryResponse
│       └── streaming_dtos.py       # StreamChunk, ReasoningStep, ToolCall
└── infrastructure/
    └── external/
        ├── mem0_memory.py          # Mem0MemoryAdapter
        └── websocket_manager.py    # WebSocketManager for streaming
```

---

## 2. Specification Drafts

### 2.1 Draft: dspy-main-agent Spec

**Purpose**: Define the main DSPy ReAct agent with conference room orchestration pattern.

**Scope**:
- MainDSPyReActAgent class with multi-signature pattern
- Tool selection and confidence scoring sub-modules
- Integration with UI and RAG specialist agents
- Streaming support with dspy.streamify()

**Locked from LLD** (agent_runtime.md:368-484):

```python
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

**Requirements**:
1. Must wrap all tools with `dspy.Tool(func, name="...", desc="...")`
2. Must implement synchronous warmup before async streaming
3. Must use `allow_reuse=True` for StreamListener with ReAct
4. Must return dspy.Prediction with: reasoning, final_answer, confidence_score, tool_calls, reasoning_steps
5. Must not exceed 150 lines per file

**Acceptance Criteria**:
- [ ] MainDSPyReActAgent compiles without errors
- [ ] All tools wrapped with dspy.Tool
- [ ] Sync warmup pattern implemented
- [ ] Returns all required prediction fields
- [ ] File under 150 lines

---

### 2.2 Draft: dspy-ui-agent Spec

**Purpose**: Define UI specialist agent for generating UI descriptors.

**Scope**:
- UIDSPyAgent with 6 UI-specific signatures
- Integration with UI descriptor contracts (from C002)
- Tool-based UI generation (render_markdown_block, render_card, etc.)

**Locked from LLD** (agent_runtime.md:486-580):

```python
class UIDSPyAgent(dspy.Module):
    """UI specialist agent for generating UI descriptors.

    Responsible for:
    - Selecting appropriate widgets
    - Configuring forms
    - Generating cards and confirmations
    - Updating progress indicators
    """

    def __init__(self):
        super().__init__()

        self.widget_selector = dspy.Predict(SelectWidgetSignature)
        self.form_configurer = dspy.Predict(ConfigureFormSignature)
        self.card_generator = dspy.Predict(ShowCardSignature)
        self.confirmation_requester = dspy.Predict(RequestConfirmationSignature)
        self.progress_updater = dspy.Predict(UpdateProgressSignature)

    def select_widget(self, content_type: str, context: str) -> dspy.Prediction:
        """Select appropriate UI widget."""

    def configure_form(self, required_fields: List[str], context: str) -> dspy.Prediction:
        """Configure form schema."""

    def show_card(self, title: str, content: str, context: str) -> dspy.Prediction:
        """Generate card widget."""

    def request_confirmation(self, action_description: str, risk_level: str) -> dspy.Prediction:
        """Request user confirmation."""

    def update_progress(self, task_name: str, current_step: int, total_steps: int) -> dspy.Prediction:
        """Update progress indicator."""
```

**Requirements**:
1. Must use UI descriptors from C002 (MarkdownBlockDescriptor, CardDescriptor, etc.)
2. Must return descriptor IDs (not full descriptor objects) from tools
3. Must not generate HTML or CSS directly
4. Must integrate with WebSocket streaming for real-time UI updates

**Acceptance Criteria**:
- [ ] All 6 signatures implemented
- [ ] Returns descriptor IDs from tools
- [ ] No HTML/CSS generation
- [ ] Integration with C002 descriptors

---

### 2.3 Draft: dspy-rag-agent Spec

**Purpose**: Define RAG specialist agent for context retrieval and injection.

**Scope**:
- RAGDSPyAgent with retrieval and injection signatures
- Agentic RAG pattern (retrieve → score → decide → filter)
- Integration with three-tier memory (Qdrant + Mem0AI)

**Locked from LLD** (agent_runtime.md:582-663):

```python
class RAGDSPyAgent(dspy.Module):
    """RAG specialist agent for context retrieval and injection.

    Agentic RAG Pattern:
    - Retrieves relevant memories
    - Scores context quality
    - Decides whether to inject
    - Filters and formats context
    """

    def __init__(self, vector_store, memory_repository):
        super().__init__()

        self._vector_store = vector_store
        self._memory_repository = memory_repository

        self.context_retriever = dspy.Predict(RetrievalSignature)
        self.injection_decider = dspy.Predict(ContextInjectionSignature)

    def retrieve_context(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> dspy.Prediction:
        """Retrieve and format context."""

    def should_inject_context(
        self,
        query: str,
        retrieved_context: str
    ) -> dspy.Prediction:
        """Decide whether to inject retrieved context."""
```

**Requirements**:
1. Must implement agentic RAG (not simple context dump)
2. Must score context quality before injection
3. Must limit retrieved memories (max 10)
4. Must filter and format context before returning

**Acceptance Criteria**:
- [ ] Agentic RAG pattern implemented
- [ ] Context quality scoring works
- [ ] Memory limit enforced (10)
- [ ] Context filtering works

---

### 2.4 Draft: langgraph-state-machines Spec

**Purpose**: Define LangGraph state machines for backend and frontend.

**Scope**:
- BackendLangGraphState with agent reasoning flow
- FrontendLangGraphState with UI component lifecycle
- State machine nodes and conditional edges
- Form interrupt/resume pattern

**Locked from LLD** (agent_runtime.md:667-819):

```python
class BackendLangGraphState(TypedDict):
    """Backend state for agent reasoning."""
    session_id: str
    user_query: str
    conversation_history: List[Dict[str, str]]
    retrieved_context: str
    reasoning_steps: List[Dict[str, Any]]
    current_step: int
    agent_status: AgentStatus  # IDLE, THINKING, USING_TOOL, COMPLETED, FAILED
    confidence_score: float
    should_continue: bool
    error_message: str

class FrontendLangGraphState(TypedDict):
    """Frontend state for UI lifecycle management."""
    session_id: str
    active_components: Dict[str, Dict[str, Any]]
    visibility_state: VisibilityState  # CHAT_VISIBLE, CHAT_MINIMIZED, CHAT_HIDDEN
    focused_component_id: str
    pending_forms: Dict[str, Dict[str, Any]]
    stream_queue: List[Dict[str, Any]]
    form_interrupt: bool
```

**Requirements**:
1. Must use TypedDict for state schemas
2. Must define nodes for each state transition
3. Must implement conditional edges for branching logic
4. Must support form interrupt/resume

**Acceptance Criteria**:
- [ ] Backend state machine compiles
- [ ] Frontend state machine compiles
- [ ] State transitions work correctly
- [ ] Form interrupt/resume works

---

## 3. API Contracts

### 3.1 REST Endpoints

| Method | Path | Request | Response | Purpose |
|--------|------|---------|----------|---------|
| POST | `/api/v1/agent/query` | `ExecuteAgentQueryCommand` | `ExecuteAgentQueryResponse` | Execute agent query (non-streaming) |
| POST | `/api/v1/agent/stream` | `ExecuteAgentQueryCommand` | Server-Sent Events | Execute agent query (streaming) |
| POST | `/api/v1/session/create` | `CreateSessionCommand` | `SessionResponseDTO` | Create new session |
| GET | `/api/v1/session/{session_id}` | - | `SessionResponseDTO` | Get session details |
| POST | `/api/v1/session/{session_id}/pause` | - | `SessionResponseDTO` | Pause session |
| POST | `/api/v1/session/{session_id}/resume` | - | `SessionResponseDTO` | Resume session |
| POST | `/api/v1/session/{session_id}/close` | - | `SessionResponseDTO` | Close session |
| POST | `/api/v1/form/submit` | `FormSubmitDTO` | `FormResponseDTO` | Submit form data |

### 3.2 WebSocket Channels

| Channel | Message Type | Schema | Purpose |
|---------|--------------|--------|---------|
| `/ws/agent/{session_id}` | TOKEN | `TokenPayload` | Stream LLM tokens |
| `/ws/agent/{session_id}` | REASONING_STEP | `ReasoningStepPayload` | Stream reasoning steps |
| `/ws/agent/{session_id}` | TOOL_CALL | `ToolCallPayload` | Stream tool invocations |
| `/ws/agent/{session_id}` | DESCRIPTOR_CREATE | `DescriptorCreatePayload` | Create UI component |
| `/ws/agent/{session_id}` | DESCRIPTOR_UPDATE | `DescriptorUpdatePayload` | Update UI component |
| `/ws/agent/{session_id}` | DESCRIPTOR_DISMISS | `DescriptorDismissPayload` | Dismiss UI component |
| `/ws/agent/{session_id}` | PROGRESS_START | `ProgressStartPayload` | Start progress indicator |
| `/ws/agent/{session_id}` | PROGRESS_UPDATE | `ProgressUpdatePayload` | Update progress |
| `/ws/agent/{session_id}` | PROGRESS_COMPLETE | `ProgressCompletePayload` | Complete progress |
| `/ws/agent/{session_id}` | FORM_SHOW | `FormShowPayload` | Show form |
| `/ws/agent/{session_id}` | FORM_SUBMIT | `FormSubmitPayload` | Submit form |
| `/ws/agent/{session_id}` | FORM_VALIDATE | `FormValidatePayload` | Validate form field |

### 3.3 Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| Main API | 8015 | FastAPI REST endpoints |
| WebSocket | 8016 | WebSocket streaming |
| Health Check | 8017 | Health check endpoint |

---

## 4. Data Model Mappings

### 4.1 Pydantic → Zod Mappings

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

### 4.2 Shared Types

**Backend (Pydantic v2)**:
```python
# application/dtos/agent_dtos.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID

class ExecuteAgentQueryCommand(BaseModel):
    session_id: UUID = Field(..., description="Session identifier")
    query: str = Field(..., min_length=1, description="User query")
    stream: bool = Field(default=False, description="Enable streaming")

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
// frontend/types/agent.ts
import { z } from "zod";

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

export const ReasoningStepSchema = z.object({
  step_number: z.number(),
  thought: z.string(),
  action: z.string().optional(),
  observation: z.string().optional(),
});

export const ToolCallSchema = z.object({
  tool_name: z.string(),
  arguments: z.record(z.any()),
  result: z.string().optional(),
  error: z.string().optional(),
  duration_ms: z.number(),
});
```

### 4.3 Enum Mappings

**Backend (Python)**:
```python
class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    USING_TOOL = "using_tool"
    COMPLETED = "completed"
    FAILED = "failed"

class SessionState(str, Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
```

**Frontend (TypeScript)**:
```typescript
export const AgentStatusSchema = z.enum([
  "idle",
  "thinking",
  "using_tool",
  "completed",
  "failed",
]);

export const SessionStateSchema = z.enum([
  "initializing",
  "active",
  "paused",
  "closed",
]);

export type AgentStatus = z.infer<typeof AgentStatusSchema>;
export type SessionState = z.infer<typeof SessionStateSchema>;
```

---

## 5. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| **C001-folder-structure** | **BLOCKING** | Defines file structure for agent/, application/, infrastructure/ layers |
| **C002-data-contracts** | **BLOCKING** | Provides UI descriptors (BaseUIDescriptor, CardDescriptor, etc.) used by UI tools |
| **C004-voice-streaming** | None | Independent; can be developed in parallel |
| **C005-memory-rag** | None | Overlaps RAG agent, but can be developed in parallel |
| **C006-release-plan** | Requires C003 | Release plan depends on completion of agent pipeline |

### Dependency Diagram

```
C001 (folder-structure)
    ↓
C002 (data-contracts) → C003 (agent-pipeline) ← Phase 2 & 4
                              ↓
                         C005 (memory-rag) ← Extends RAG agent
                              ↓
                         C006 (release-plan)
```

---

**Next Artifact**: validate.md
