# Scan Artifact: c003-agent-pipeline

**Generated**: 2026-01-28
**Change**: c003-agent-pipeline
**Schema**: spec-factory v1

---

## 1. LLD Synthesis

### 1.1 Relevant LLD Documents

| Document | Path | Relevance |
|----------|------|-----------|
| Agent Runtime LLD | `docs/engineering/lld/agent_runtime.md` | **PRIMARY** - Defines DSPy signatures, tools, agents, LangGraph state machines (LOCKED) |
| Domain Model LLD | `docs/engineering/lld/domain_model.md` | **PRIMARY** - Defines entities: AgentSessionEntity, UIComponentEntity, MemoryConsolidationEntity (LOCKED) |
| Incremental Release Plan | `docs/engineering/lld/incremental_release_plan.md` | **PRIMARY** - Phase 2 (Main Agent), Phase 4 (State Machines), Phase 5 (Memory+RAG) (LOCKED) |
| DSPy + Mem0AI Research | `docs/research/02_dspy_mem0_integration.md` | **SECONDARY** - Memory integration patterns, ReAct with memory |

### 1.2 Locked Definitions from LLD

#### DSPy Signatures (agent_runtime.md:19-137)

**Main Signatures**:
```python
class MainAgentSignature(dspy.Signature):
    user_query: str = dspy.InputField(desc="User's query or request")
    conversation_history: List[str] = dspy.InputField(desc="Conversation history")
    retrieved_context: str = dspy.InputField(desc="Retrieved context from RAG")
    reasoning: str = dspy.OutputField(desc="Step-by-step reasoning process")
    final_answer: str = dspy.OutputField(desc="Final response to user")

class ToolSelectionSignature(dspy.Signature):
    query_analysis: str = dspy.InputField(desc="Analysis of user query")
    available_tools: List[str] = dspy.InputField(desc="List of available tool names")
    selected_tools: List[str] = dspy.OutputField(desc="Tools to use for this query")
    tool_rationale: str = dspy.OutputField(desc="Reasoning for tool selection")

class ConfidenceScoringSignature(dspy.Signature):
    response: str = dspy.InputField(desc="Generated response")
    context_quality: str = dspy.InputField(desc="Quality of retrieved context")
    confidence_score: float = dspy.OutputField(desc="Confidence from 0.0 to 1.0")
    confidence_reasoning: str = dspy.OutputField(desc="Explanation of confidence score")
```

**UI Signatures**:
```python
class SelectWidgetSignature(dspy.Signature)
class ConfigureFormSignature(dspy.Signature)
class ShowCardSignature(dspy.Signature)
class RequestConfirmationSignature(dspy.Signature)
class UpdateProgressSignature(dspy.Signature)
```

**RAG Signatures**:
```python
class RetrievalSignature(dspy.Signature)
class ContextInjectionSignature(dspy.Signature)
```

#### DSPy Tools (agent_runtime.md:142-346)

**Main Tools**:
- `safe_calculator(expression: str) -> str` - AST-based math evaluation
- `searxng_search(query: str) -> str` - Web search via SearXNG
- `get_current_weather(location: str) -> str` - Weather via wttr.in
- `company_mis_search(query: str) -> str` - Company data placeholder

**UI Tools**:
- `render_markdown_block(text: str) -> str` - Returns UI descriptor ID
- `render_card(title, content, actions) -> str` - Returns UI descriptor ID
- `request_confirmation(action_description, risk_level) -> str` - Returns UI descriptor ID
- `update_progress(task_name, progress_percent) -> str` - Returns UI descriptor ID

#### DSPy Agents (agent_runtime.md:350-663)

**Main DSPy ReAct Agent**:
```python
class MainDSPyReActAgent(dspy.Module):
    """Conference Room Pattern: CEO orchestrates UI and RAG specialists."""

    def __init__(
        self,
        tools: List[dspy.Tool],
        max_iters: int = 8,
        confidence_threshold: float = 0.7
    ):
        self.tool_selector = dspy.Predict(ToolSelectionSignature)
        self.confidence_scorer = dspy.Predict(ConfidenceScoringSignature)
        self.react = dspy.ReAct(MainAgentSignature, tools=tools, max_iters=max_iters)

    def forward(
        self,
        user_query: str,
        conversation_history: List[str],
        retrieved_context: str = ""
    ) -> dspy.Prediction:
        # Returns: reasoning, final_answer, confidence_score, tool_calls, reasoning_steps

    async def execute(
        self,
        user_query: str,
        conversation_history: List[str],
        retrieved_context: str,
        ui_callback: Optional[Callable] = None
    ) -> dspy.Prediction:
        # Execute with optional UI callback for streaming
```

**UI DSPy Agent**:
```python
class UIDSPyAgent(dspy.Module):
    """UI specialist for generating UI descriptors."""
    # 6 signatures: SelectWidget, ConfigureForm, ShowCard, RequestConfirmation, UpdateProgress
```

**RAG DSPy Agent**:
```python
class RAGDSPyAgent(dspy.Module):
    """RAG specialist for context retrieval and injection."""
    # Agentic RAG: retrieves, scores, decides injection, filters
```

#### LangGraph State Machines (agent_runtime.md:667-819)

**Backend State**:
```python
class BackendLangGraphState(TypedDict):
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
```

**Frontend State**:
```python
class FrontendLangGraphState(TypedDict):
    session_id: str
    active_components: Dict[str, Dict[str, Any]]
    visibility_state: VisibilityState  # CHAT_VISIBLE, CHAT_MINIMIZED, CHAT_HIDDEN
    focused_component_id: str
    pending_forms: Dict[str, Dict[str, Any]]
    stream_queue: List[Dict[str, Any]]
    form_interrupt: bool
```

#### Entities (domain_model.md:23-269)

**AgentSessionEntity**:
```python
@dataclass
class AgentSessionEntity:
    session_id: UUID
    user_id: str  # SHA-256 hash
    state: SessionState  # INITIALIZING, ACTIVE, PAUSED, CLOSED
    created_at: datetime
    modified_at: datetime
    last_activity_at: datetime
    current_reasoning_step: int = 0
    total_tool_calls: int = 0

    # Business methods: is_active(), pause(), resume(), close(),
    # increment_reasoning_step(), increment_tool_calls(), update_activity()
```

**UIComponentEntity**:
```python
@dataclass
class UIComponentEntity:
    component_id: UUID
    session_id: UUID
    component_type: UIComponentType
    state: UIComponentState  # CREATING, CREATED, UPDATING, DISMISSED
    descriptor: BaseUIDescriptor
    created_at: datetime
    updated_at: datetime
    dismissed_at: Optional[datetime] = None

    # Business methods: is_dismissible(), dismiss(), update_descriptor(),
    # mark_created(), is_visible(), age_seconds()
```

**MemoryConsolidationEntity**:
```python
@dataclass
class MemoryConsolidationEntity:
    consolidation_id: UUID
    session_id: UUID
    trigger: ConsolidationTrigger  # SCHEDULED, MANUAL, PRE_QUERY
    status: ConsolidationStatus  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    memories_processed: int = 0
    memories_merged: int = 0
    memories_invalidated: int = 0
    error_message: Optional[str] = None

    # Business methods: start(), complete(), fail(), duration_seconds(), merge_rate()
```

#### Enums (domain_model.md:346-412)

```python
class SessionState(str, Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"

class UIComponentType(str, Enum):
    MARKDOWN = "markdown"
    CARD = "card"
    FORM = "form"
    PROGRESS = "progress"
    ACTION = "action"
    CONFIRMATION = "confirmation"
    VOICE = "voice"

class UIComponentState(str, Enum):
    CREATING = "creating"
    CREATED = "created"
    UPDATING = "updating"
    DISMISSED = "dismissed"

class ConsolidationTrigger(str, Enum):
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    PRE_QUERY = "pre_query"

class ConsolidationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    USING_TOOL = "using_tool"
    COMPLETED = "completed"
    FAILED = "failed"

class VisibilityState(str, Enum):
    CHAT_VISIBLE = "chat_visible"
    CHAT_MINIMIZED = "chat_minimized"
    CHAT_HIDDEN = "chat_hidden"
```

#### Repository Interfaces (domain_model.md:418-592)

**AgentSessionRepository**:
```python
class AgentSessionRepository(ABC):
    async def get_by_id(self, session_id: UUID) -> Optional[AgentSessionEntity]
    async def get_by_user_id(self, user_id: str) -> List[AgentSessionEntity]
    async def get_active_sessions(self, user_id: str) -> List[AgentSessionEntity]
    async def create(self, session: AgentSessionEntity) -> AgentSessionEntity
    async def update(self, session: AgentSessionEntity) -> AgentSessionEntity
    async def delete(self, session_id: UUID) -> bool
    async def exists(self, session_id: UUID) -> bool
```

**UIComponentRepository**:
```python
class UIComponentRepository(ABC):
    async def get_by_id(self, component_id: UUID) -> Optional[UIComponentEntity]
    async def get_by_session_id(self, session_id: UUID) -> List[UIComponentEntity]
    async def get_visible_components(self, session_id: UUID) -> List[UIComponentEntity]
    async def create(self, component: UIComponentEntity) -> UIComponentEntity
    async def update(self, component: UIComponentEntity) -> UIComponentEntity
    async def dismiss(self, component_id: UUID) -> bool
    async def dismiss_by_session(self, session_id: UUID) -> int
    async def delete(self, component_id: UUID) -> bool
```

**MemoryRepository**:
```python
class MemoryRepository(ABC):
    async def store_memory(
        self,
        content: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID
    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]
    async def update_memory(self, memory_id: UUID, new_content: str) -> bool
    async def delete_memory(self, memory_id: UUID) -> bool
    async def consolidate_memories(
        self,
        session_id: UUID,
        user_id: str
    ) -> MemoryConsolidationEntity
```

---

## 2. Codebase Exploration (opsx:explore)

### 2.1 Exploration Topics

**Forced Topics**:
1. **DSPy ReAct patterns** - Multi-signature agents, tool wrapping, streaming
2. **LangGraph state machines** - TypedDict state, node functions, conditional edges
3. **Conference Room orchestration** - CEO agent with UI and RAG specialists
4. **Streaming with dspy.streamify()** - Sync warmup, async streaming, WebSocket integration
5. **Memory integration** - Mem0AI, RAG patterns, consolidation

### 2.2 File Inventory

#### Backend Files (Prototypes)

| File | Lines | Purpose |
|------|-------|---------|
| `prototypes/R011_personal_assistant/backend/service.py` | 216 | DSPy ReAct + Voice integration |
| `prototypes/R013_travel_planning_stream/backend/dspy_service.py` | 107 | LM configuration, warmup pattern |
| `prototypes/R013_travel_planning_stream/backend/travel_react.py` | 148 | ReAct with streaming, dspy.streamify() |
| `prototypes/R014_ui_showcase/backend/master_agent.py` | 147 | Conference Room pattern (CEO orchestrator) |
| `prototypes/R014_ui_showcase/backend/services/pipeline/multihop_reader.py` | 144 | Multi-hop reasoning specialist |
| `prototypes/R013_travel_planning_stream/backend/websocket.py` | 120 | WebSocket streaming integration |

#### Frontend Files (Prototypes)

| File | Lines | Purpose |
|------|-------|---------|
| `prototypes/R013_travel_planning_stream/frontend/src/app/page.tsx` | 180 | Streaming token display |
| `prototypes/R014_ui_showcase/frontend/src/types/widget-types.ts` | 250 | UI descriptor type definitions |

#### Documentation Files

| File | Lines | Purpose |
|------|-------|---------|
| `docs/research/02_dspy_mem0_integration.md` | 479 | Memory-enabled ReAct patterns |
| `docs/engineering/lld/agent_runtime.md` | 824 | LOCKED: All DSPy and LangGraph definitions |
| `docs/engineering/lld/domain_model.md` | 676 | LOCKED: All entities and repositories |

---

## 3. Patterns Discovered

### 3.1 Architectural Patterns

**Conference Room Pattern** (R014):
- **CEO Agent** (MainDSPyReActAgent) orchestrates specialist agents
- **UI Specialist** (UIDSPyAgent) handles widget generation
- **RAG Specialist** (RAGDSPyAgent) handles context retrieval
- Specialists exposed as tools to CEO via `dspy.Tool` wrapper

**Clean Architecture Layers**:
```
domain/          # Entities (@dataclass), Repository interfaces (ABC)
infrastructure/  # Adapters (Redis, Qdrant, Mem0AI)
agent/           # DSPy signatures, tools, agents
application/     # Use cases, DTOs, services
presentation/    # FastAPI routes, WebSocket endpoints
```

**LangGraph Integration**:
- DSPy agents wrapped as LangGraph nodes
- State machines manage agent lifecycle
- Backend state: agent reasoning flow
- Frontend state: UI component lifecycle

### 3.2 Code Patterns

**DSPy Tool Wrapping** (CRITICAL):
```python
# WRONG: Direct function passing
self.react = dspy.ReAct(signature, tools=[my_function])

# RIGHT: Wrap with dspy.Tool
search_tool = dspy.Tool(
    search_travel,
    name="search_travel",
    desc="Search for current travel information..."
)
self.react = dspy.ReAct(signature, tools=[search_tool])
```

**Streaming Pattern** (CRITICAL):
```python
# Step 1: Synchronous warmup (REQUIRED!)
agent = MainDSPyReActAgent(tools=tools)
_ = agent(user_query="warmup", conversation_history=[], retrieved_context="")

# Step 2: Wrap with streamify
stream_agent = dspy.streamify(
    agent,
    stream_listeners=[
        dspy.streaming.StreamListener(
            signature_field_name="next_thought",
            allow_reuse=True  # Required for ReAct loops
        )
    ]
)

# Step 3: Async iteration
async for chunk in stream_agent(question=user_query):
    # Process chunks
```

**Session Management Pattern**:
```python
# Server-side session storage
class SessionManager:
    async def get_or_create_session(self, session_id: str) -> AgentSession:
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        return await self.create_session(session_id)

    async def update_history(self, session_id: str, role: str, content: str):
        session = await self.get_or_create_session(session_id)
        session.history.append({"role": role, "content": content})
```

**Memory Integration Pattern**:
```python
# Agentic RAG (not simple dump)
class RAGDSPyAgent(dspy.Module):
    def forward(self, query: str, user_id: str):
        # Step 1: Retrieve memories
        memories = await self._memory_repo.search_memories(query, user_id, limit=10)

        # Step 2: Decide whether to inject context
        decision = self.injection_decider(query=query, retrieved_context=memories)

        # Step 3: Filter and format if needed
        if decision.should_inject:
            return decision.filtered_context
        return ""
```

### 3.3 Anti-Patterns to Avoid

**❌ Anti-Pattern 1: Skipping Warmup**
```python
# WRONG: Async streaming without warmup fails
async for chunk in stream_agent(question=user_query):
    pass  # Will raise error!

# RIGHT: Always warm up synchronously first
_ = agent(question="warmup", history=[], context="")
async for chunk in stream_agent(question=user_query):
    pass  # Works!
```

**❌ Anti-Pattern 2: Unwrapped Tools**
```python
# WRONG: Tool hallucinates arguments
self.react = dspy.ReAct(signature, tools=[calculator])

# RIGHT: Tool has explicit schema
calc_tool = dspy.Tool(calculator, name="calculator", desc="Safe math evaluator")
self.react = dspy.ReAct(signature, tools=[calc_tool])
```

**❌ Anti-Pattern 3: Using History Object Directly**
```python
# WRONG: History object is not a list
result = agent(question=q, history=session.history)  # Type error!

# RIGHT: Use messages attribute
result = agent(question=q, history=session.history.messages)
```

**❌ Anti-Pattern 4: Large Monolithic Files**
```python
# WRONG: 500-line agent file with everything
class MegaAgent:  # 500+ lines

# RIGHT: Split into focused files
# agent/dspy_agents/main_react_agent.py (120 lines)
# agent/dspy_agents/ui_agent.py (80 lines)
# agent/dspy_agents/rag_agent.py (80 lines)
```

**❌ Anti-Pattern 5: Mixed Concerns**
```python
# WRONG: UI logic in agent
class Agent:
    def generate_ui(self):  # UI logic doesn't belong here
        return {"html": "<div>...</div>"}

# RIGHT: Agent returns descriptor ID, UI layer renders
class Agent:
    def request_confirmation(self, action: str) -> str:
        return f"CONFIRMATION:{uuid4()}"  # Descriptor ID only
```

---

## 4. Reference Analysis

### 4.1 Mimicus Patterns (Copy Concepts, Not Names)

| Concept | Mimicus Pattern | Intended Use |
|---------|-----------------|--------------|
| Repository | ABC base class + implementations | `AgentSessionRepository`, `MemoryRepository` |
| Entity | `@dataclass` with business methods | `AgentSessionEntity`, `UIComponentEntity` |
| Use Case | Single-purpose classes with `execute()` | `ExecuteAgentQueryUseCase`, `StreamUIUpdateUseCase` |
| DTO | Pydantic models for API layer | `ExecuteAgentQueryCommand`, `ExecuteAgentQueryResponse` |
| File Size | Max 100 lines executable + 50 overhead | All agent files under 150 lines |

### 4.2 R013 Reference (Streaming Patterns)

| Concept | R013 Approach | Improved Approach |
|---------|---------------|-------------------|
| Warmup | Explicit sync call before async | Keep pattern, document as REQUIRED |
| StreamListener | `allow_reuse=True` for ReAct | Keep same, prevents memory leaks |
| Chunk handling | Collect and build final response | Add token streaming via WebSocket |
| Error handling | Basic try/except | Add structured error reporting |

### 4.3 R014 Reference (Conference Room Pattern)

| Concept | R014 Approach | Improved Approach |
|---------|---------------|-------------------|
| Agent structure | Separate files for specialists | Keep same, improves modularity |
| Tool wrapping | `dspy.Tool` with explicit names | Keep same, prevents hallucination |
| QA checkpoints | Manual validation | Add confidence scoring |

---

## 5. Key Files for This Change

```
# LLD Definitions (LOCKED - Source of Truth)
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/agent_runtime.md
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/domain_model.md
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/incremental_release_plan.md

# Research Documents
/home/riju279/Documents/Code/XRIG/AgentX/docs/research/02_dspy_mem0_integration.md

# Prototype References (Concepts Only)
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R011_personal_assistant/
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/

# DSPy Tutorials (External Reference)
/home/riju279/Downloads/dspy-main/dspy-main/docs/tutorials/
```

---

**Next Artifact**: extract.md
