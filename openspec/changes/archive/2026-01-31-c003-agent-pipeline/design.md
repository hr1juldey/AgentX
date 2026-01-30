# Design Artifact: c003-agent-pipeline

**Generated**: 2026-01-28
**Change**: c003-agent-pipeline
**Schema**: spec-factory v1

---

## 1. Architecture

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Agent Pipeline Architecture                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Frontend (Next.js)                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ Chat UI      │  │ Card Display │  │ Form Handler │          │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │   │
│  │         │                  │                  │                   │   │
│  │         └──────────────────┼──────────────────┘                   │   │
│  │                            │                                      │   │
│  │                    ┌───────▼────────┐                             │   │
│  │                    │ WebSocket (ws) │                             │   │
│  │                    └───────┬────────┘                             │   │
│  └────────────────────────────┼────────────────────────────────────┘   │
│                                 │                                        │
│  ┌────────────────────────────▼────────────────────────────────────┐   │
│  │                      Backend (FastAPI)                           │   │
│  │                                                                 │   │
│  │  ┌─────────────────────────────────────────────────────────┐    │   │
│  │  │              Presentation Layer (API)                    │    │   │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │    │   │
│  │  │  │ Agent      │  │ Session    │  │ Form       │         │    │   │
│  │  │  │ Routes     │  │ Routes     │  │ Routes     │         │    │   │
│  │  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘         │    │   │
│  │  └────────┼───────────────┼───────────────┼─────────────────┘    │   │
│  │           │               │               │                      │   │
│  │  ┌────────▼───────────────▼───────────────▼─────────────────┐    │   │
│  │  │             Application Layer (Orchestration)             │    │   │
│  │  │                                                          │    │   │
│  │  │  ┌─────────────────┐  ┌─────────────────┐               │    │   │
│  │  │  │ AgentOrchestrator│  │  UIService     │               │    │   │
│  │  │  │ (coordinates    │  │  (form         │               │    │   │
│  │  │  │  state machines)│  │   interrupt)   │               │    │   │
│  │  │  └────────┬────────┘  └────────┬────────┘               │    │   │
│  │  │           │                    │                          │    │   │
│  │  │  ┌────────▼────────────────────▼─────────────────┐       │    │   │
│  │  │  │         Use Cases                                │       │    │   │
│  │  │  │  ┌────────────────┐  ┌────────────────┐         │       │    │   │
│  │  │  │  │ExecuteAgent    │  │StreamUIUpdate  │         │       │    │   │
│  │  │  │  │QueryUseCase    │  │UseCase         │         │       │    │   │
│  │  │  │  └────────┬────────┘  └────────┬────────┘         │       │    │   │
│  │  │  └───────────┼───────────────────┼─────────────────────┘       │    │   │
│  │  └──────────────┼───────────────────┼─────────────────────────────┘    │   │
│  │                 │                   │                                  │   │
│  │  ┌──────────────▼───────────────────▼───────────────────────────┐    │   │
│  │  │                   Agent Layer (DSPy)                           │    │   │
│  │  │                                                               │    │   │
│  │  │  ┌─────────────────────────────────────────────────────┐    │    │   │
│  │  │  │        Conference Room Pattern (CEO + Specialists)   │    │    │   │
│  │  │  │                                                         │    │   │
│  │  │  │  ┌──────────────────┐  ┌──────────────────┐          │    │   │
│  │  │  │  │ MainDSPyReAct    │  │ Specialist Tools │          │    │   │
│  │  │  │  │ Agent (CEO)      │◀─┤  ┌───────────┐   │          │    │   │
│  │  │  │  │                  │  │  │UI Agent   │   │          │    │   │
│  │  │  │  │ • ToolSelector   │  │  └───────────┘   │          │    │   │
│  │  │  │  │ • ConfidenceScore│  │  ┌───────────┐   │          │    │   │
│  │  │  │  │ • ReAct Loop     │  │  │RAG Agent  │   │          │    │   │
│  │  │  │  └──────────────────┘  │  └───────────┘   │          │    │   │
│  │  │  └──────────────────────────┴─────────────────────┘          │    │   │
│  │  │                                                               │    │   │
│  │  │  ┌─────────────────┐  ┌─────────────────┐                   │    │   │
│  │  │  │ State Machines  │  │ Tools           │                   │    │   │
│  │  │  │ • Backend State  │  │ • Calculator    │                   │    │   │
│  │  │  │ • Frontend State │  │ • Search        │                   │    │   │
│  │  │  └─────────────────┘  │ • Weather       │                   │    │   │
│  │  └───────────────────────┴─────────────────┘                   │    │   │
│  └───────────────────────────────┬─────────────────────────────────────┘   │
│                                  │                                        │
│  ┌───────────────────────────────▼─────────────────────────────────────┐   │
│  │                      Infrastructure Layer                          │   │
│  │                                                                     │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │   │
│  │  │ Qdrant          │  │ Mem0AI          │  │ Redis           │     │   │
│  │  │ (Tier 2 Memory) │  │ (Tier 3 Memory) │  │ (Sessions)      │     │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Layer Structure (Clean Architecture + LangGraph Server-Driven UI)

```
agentx/
├── core/                           # Configuration & DI
│   ├── config.py                   # Pydantic Settings
│   └── dependencies.py             # Singletons (get_settings(), get_lm())
│
├── domain/                         # Business logic (no external deps)
│   ├── entities/
│   │   ├── agent_session.py        # AgentSessionEntity
│   │   ├── ui_component.py         # UIComponentEntity
│   │   ├── memory_consolidation.py # MemoryConsolidationEntity
│   │   └── enums.py                # All enums (AgentStatus, SessionState, etc.)
│   ├── repositories/
│   │   ├── agent_session_repository.py  # ABC + implementations
│   │   ├── ui_component_repository.py   # ABC + in-memory implementation
│   │   └── memory_repository.py          # ABC + implementations
│   └── services/
│       └── validation.py           # ValidationService
│
├── agent/                          # DSPy agents + LangGraph StateGraph
│   ├── __init__.py                  # Package init
│   ├── graph.py                     # LangGraph StateGraph with ui_message_reducer
│   ├── state.py                     # AgentState TypedDict with UI tracking
│   ├── ui.tsx                       # React components (colocated!)
│   │                              # └── Export default {component, ...}
│   ├── nodes/                       # LangGraph nodes
│   │   ├── analyst.py               # Query understanding
│   │   ├── designer.py              # UI widget selection (state aware!)
│   │   ├── researcher.py            # Web search
│   │   ├── contextualizer.py        # Rerank + filter
│   │   └── writer.py                # Content generation
│   ├── dspy_signatures/
│   │   ├── main_signatures.py      # MainAgentSignature, ToolSelectionSignature
│   │   ├── ui_signatures.py        # SelectWidgetSignature (from R014)
│   │   └── rag_signatures.py       # RetrievalSignature, ContextInjectionSignature
│   ├── tools/
│   │   ├── main_tools.py           # safe_calculator, searxng_search
│   │   └── ui_tools.py             # (Replaced by push_ui_message)
│   ├── dspy_agents/
│   │   ├── main_react_agent.py     # MainDSPyReActAgent (CEO orchestrator)
│   │   ├── ui_agent.py             # UIDSPyAgent (UI specialist)
│   │   └── rag_agent.py            # RAGDSPyAgent (RAG specialist)
│   └── langgraph/
│       ├── backend_state_machine.py    # BackendLangGraphState, workflow
│       └── frontend_state_machine.py   # FrontendLangGraphState, workflow
│
├── langgraph.json                  # Graph + UI component mapping
│
├── application/                    # Use case orchestration
│   ├── use_cases/
│   │   ├── execute_agent_query.py  # ExecuteAgentQueryUseCase
│   │   └── stream_ui_update.py     # (Replaced by LangGraph SDK)
│   ├── services/
│   │   ├── agent_orchestrator.py   # Coordinates state machines + agents
│   │   └── ui_service.py           # Form interrupt/resume logic
│   └── dtos/
│       ├── agent_dtos.py           # ExecuteAgentQueryCommand, ExecuteAgentQueryResponse
│       ├── streaming_dtos.py       # StreamChunk, ReasoningStep, ToolCall
│       └── session_dtos.py         # CreateSessionCommand, SessionResponseDTO
│
├── infrastructure/                 # External concerns
│   ├── database/
│   │   ├── redis_session_adapter.py    # RedisSessionAdapter
│   │   ├── sqlite_session_adapter.py   # SQLiteSessionAdapter
│   │   └── qdrant_vector_store.py      # QdrantVectorStoreAdapter
│   └── external/
│       ├── mem0_memory.py          # Mem0MemoryAdapter
│       └── websocket_manager.py    # (Replaced by LangGraph server)
│
└── presentation/                   # FastAPI routes
    └── api/
        └── v1/
            ├── agent_routes.py    # /api/v1/agent/query (uses LangGraph SDK)
            └── session_routes.py  # /api/v1/session/*
```

### 1.2.1 LangGraph Server-Driven UI Architecture (from C007)

**AgentState with UI tracking**:
```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.ui import AnyUIMessage, ui_message_reducer

class AgentState(TypedDict):
    """Agent state with UI message tracking."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]
    # ^ ui_message_reducer automatically manages UI state
    query: str
    user_id: str
    context: list[str]
```

**Component colocation**:
```
agent/
├── graph.py         # StateGraph with ui_message_reducer
├── state.py         # AgentState TypedDict
├── ui.tsx           # React components (colocated!)
└── nodes/
    └── designer.py  # UI widget selection with state awareness
```

**Designer node with state awareness** (fixes R014 problem):
```python
from langgraph.graph.ui import push_ui_message
from uuid import uuid4

async def designer_node(state: AgentState):
    """Designer node with state awareness (R014 fix)."""
    # Check existing widgets (state awareness!)
    existing_widgets = [msg.name for msg in state.ui]

    # Select complementary widget (not repeat)
    if "card" not in existing_widgets:
        push_ui_message(
            "card",
            {
                "title": "Analysis Complete",
                "content": "Found 5 relevant results...",
            },
            message=state["messages"][-1]
        )

    return {"ui": state["ui"]}  # ui_message_reducer handles merge
```

**Streaming with merge pattern**:
```python
async def writer_node(state: AgentState):
    """Stream content updates to same UI message."""
    # Create initial UI message
    ui_message = push_ui_message(
        "writer",
        {"title": "Generating response..."},
        message=state["messages"][-1]
    )
    ui_message_id = ui_message["id"]

    # Stream updates (merge props)
    for chunk in content_stream:
        push_ui_message(
            "writer",
            {"content": chunk.text},  # New content
            id=ui_message_id,  # Same ID!
            merge=True,  # Merge props!
            message=state["messages"][-1],
        )

    return {"ui": state["ui"]}
```

**Component export (ui.tsx)**:
```typescript
export default {
  markdown: MarkdownComponent,
  card: CardComponent,
  form: FormComponent,
  progress: ProgressComponent,
  action: ActionComponent,
  confirmation: ConfirmationComponent,
  image: ImageComponent,
  gallery: GalleryComponent,
  chart: ChartComponent,
  searchResult: SearchResultComponent,
  hopProgress: HopProgressComponent,
  citationCard: CitationCardComponent,
};
```

**langgraph.json mapping**:
```json
{
  "graphs": {
    "agent": "./agent/graph.py"
  },
  "ui": {
    "agent": "./agent/ui.tsx"
  }
}
```

**Rationale** (from C007 exploration):
- Designer agent gets state awareness (fixes R014's repeating widgets problem)
- Components colocated with graph code (industry standard: LangSmith)
- Shadow DOM for style isolation (guaranteed no conflicts)
- Backend has full control (code + data delivery)

---

## 2. Data Flow

### 2.1 Agent Query Flow (Non-Streaming)

```
┌─────────┐    POST /api/v1/agent/query    ┌──────────────┐
│ Client  │────────────────────────────────▶│ FastAPI      │
└─────────┘                                   │ Route        │
                                              └──────┬───────┘
                                                     │
                     ┌───────────────────────────────▼────────────────────┐
                     │         ExecuteAgentQueryUseCase.execute()         │
                     │                                                       │
                     │  1. Validate session                                  │
                     │  2. RAGDSPyAgent.retrieve_context(user_id, query)    │
                     │     └─→ MemoryRepository.search_memories()           │
                     │         └─→ Qdrant/Mem0AI                              │
                     │  3. RAGDSPyAgent.should_inject_context()             │
                     │  4. BackendLangGraphState.ainvoke(initial_state)     │
                     │     └─→ MainDSPyReActAgent.forward()                 │
                     │         ├─→ ToolSelector (optional)                  │
                     │         ├─→ ReAct loop (max 8 iters)                  │
                     │         │   ├─→ UIDSPyAgent.show_card()              │
                     │         │   └─→ safe_calculator()                    │
                     │         └─→ ConfidenceScorer                          │
                     │  5. Return ExecuteAgentQueryResponse                 │
                     └───────────────────────────────┬────────────────────┘
                                                     │
                                              ┌──────▼───────┐
                                              │ 200 JSON     │
                                              │ Response     │
                                              └──────┬───────┘
                                                     │
                                              ┌──────▼───────┐
                                              │ Client       │
                                              │ Display UI   │
                                              └──────────────┘
```

### 2.2 Agent Query Flow (LangGraph Server-Driven UI)

```
┌─────────┐    useStream() hook           ┌──────────────┐
│ Client  │────────────────────────────────▶│ LangGraph    │
│ (Next.js)│◀────────────────────────────────│ Server       │
└─────────┘    (port 2024)                 │ (port 2024)  │
                                              └──────┬───────┘
                                                     │
                     ┌───────────────────────────────▼────────────────────┐
                     │            LangGraph StateGraph                      │
                     │                                                       │
                     │  1. analyst_node: Query understanding              │
                     │  2. researcher_node: Web search (optional)          │
                     │  3. contextualizer_node: Rerank + filter             │
                     │  4. designer_node: UI widget selection              │
                     │     └─→ push_ui_message("card", {...})               │
                     │  5. writer_node: Content generation                 │
                     │     └─→ push_ui_message("writer", {...})             │
                     │     └─→ Streaming with merge=True                   │
                     │                                                       │
                     │  All nodes access state.ui for state awareness!      │
                     └───────────────────────────────┬────────────────────┘
                                                     │
                                    onCustomEvent() │
                                                     │
┌────────────────────────────────────▼─────────────────────────────────┐
│                    Frontend Processes UI Events                       │
│                                                                      │
│  • onCustomEvent callback receives AnyUIMessage                       │
│  • uiMessageReducer(prev.ui, event) updates state                     │
│  • LoadExternalComponent fetches and renders component               │
│  • Component uses Shadow DOM for style isolation                     │
│                                                                      │
│  Example:                                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ {values.ui?.map((ui) => (                                     │   │
│  │   <LoadExternalComponent                                     │   │
│  │     key={ui.id}                                              │   │
│  │     stream={thread}                                          │   │
│  │     message={ui}                                              │   │
│  │     fallback={<SkeletonWidget />}                             │   │
│  │   />                                                         │   │
│  │ ))}                                                         │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  No WebSocket code needed - LangGraph SDK handles everything!        │
└──────────────────────────────────────────────────────────────────────┘
```

**Key Changes from R014 Pattern**:
- ❌ Old: WebSocket + descriptor-only + nested callbacks
- ✅ New: LangGraph SDK + server-driven UI + state-based

**Designer Agent State Awareness** (fixes R014 problem):
```python
# R014 problem: Designer sent same widgets repeatedly
# Solution: state.ui tracks all shown widgets

async def designer_node(state: AgentState):
    existing_widgets = [msg.name for msg in state.ui]  # State awareness!

    if "card" not in existing_widgets:
        push_ui_message("card", {...})  # Emit card

    return {"ui": state["ui"]}  # ui_message_reducer handles merge
```

**Streaming with Merge**:
```python
# Progressive updates to same UI message
ui_message = push_ui_message("writer", {"title": "..."})
ui_message_id = ui_message["id"]

for chunk in content_stream:
    push_ui_message(
        "writer",
        {"content": chunk.text},  # New content
        id=ui_message_id,  # Same ID!
        merge=True,  # Merge props!
    )
```

### 2.3 Form Interrupt/Resume Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Form Interrupt Flow                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Agent needs user input                                      │
│     ┌─→ MainDSPyReActAgent determines form needed              │
│     └─→ UIDSPyAgent.configure_form() generates FormDescriptor  │
│                                                                 │
│  2. Backend state machine triggers interrupt                   │
│     ┌─→ FrontendLangGraphState: form_interrupt = True         │
│     └─→ WebSocket: FORM_SHOW message sent                     │
│                                                                 │
│  3. Frontend displays form, pauses execution                    │
│     ┌─→ Render form from FormDescriptor                        │
│     └─→ Backend state machine waits                            │
│                                                                 │
│  4. User submits form                                          │
│     ┌─→ POST /api/v1/form/submit with form_data                │
│     └─→ UIService.on_form_submit(session_id, form_data)       │
│                                                                 │
│  5. Resume agent execution                                      │
│     ┌─→ FrontendLangGraphState: form_interrupt = False        │
│     └─→ BackendLangGraphState continues with form data        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| **Agent Orchestration** | Conference Room Pattern (CEO + specialists) | Single monolithic agent | Separation of concerns; easier to test and maintain |
| **Tool Wrapping** | `dspy.Tool(func, name="...", desc="...")` required | Direct function passing | Prevents argument hallucination by LLM |
| **Streaming Pattern** | `dspy.streamify()` with `StreamListener(allow_reuse=True)` | Manual iteration | Cleaner API; proven pattern from R013 |
| **Sync Warmup** | Required before async streaming | Skip warmup | DSPy architecture requirement; prevents errors |
| **State Management** | LangGraph TypedDict with `ui_message_reducer` | Manual state tracking | Declarative; visualizable; built-in error handling |
| **RAG Approach** | Agentic (retrieve → score → decide → filter) | Simple context dump | Better context quality; avoids injection failures |
| **UI Architecture** | **LangGraph server-driven UI** | R014 descriptor-only, React-only | **Backend has full control; state awareness; Shadow DOM (C007)** |
| **Component Placement** | **Colocated with graph (ui.tsx)** | Separate frontend repo | **Industry standard (LangSmith); single source of truth (C007)** |
| **State Tracking** | **ui_message_reducer** | Zustand atomic slices | **Automatic state tracking; Designer agent awareness (C007)** |
| **Style Isolation** | **Shadow DOM** | Global CSS, CSS-in-JS | **Guaranteed isolation; no style conflicts (C007)** |
| **Frontend Rendering** | `LoadExternalComponent` | Descriptor rendering | Server-driven UI; type-safe; automatic bundling |
| **File Organization** | Split agents (main, ui, rag) + nodes/ | Single large agent file | Keeps files under 150 lines; improves maintainability |

### 3.1 R014 Migration Strategy (from C007)

**Architectural Shift: Callbacks → State**

| Aspect | R014 Pattern | LangGraph Pattern |
|--------|--------------|-------------------|
| **State Management** | Zustand atomic slices (manual) | `ui_message_reducer` (automatic) |
| **Widget Delivery** | WebSocket + UIDescriptor (data only) | `LoadExternalComponent` (code + data) |
| **Callbacks** | Nested functions (hard to test) | State-based (testable, traceable) |
| **Component Location** | Frontend only | Colocated with graph (`ui.tsx`) |
| **Style Isolation** | Global CSS | Shadow DOM (guaranteed) |
| **Designer Agent** | No state awareness (repeated widgets) | `state.ui` tracks all shown widgets |

**Backend Pattern Migration**:
```python
# R014 Pattern (callback-based):
use_case = get_master_agent_use_case()
master_agent, delivery_plan_type = use_case.setup_master_agent_with_pipeline(
    widget_callback=send_widget,  # Nested callback
    qa_callback=send_qa_progress,
)

# LangGraph Pattern (state-based):
class AgentState(TypedDict):
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]

async def designer_node(state: AgentState):
    existing_widgets = [msg.name for msg in state.ui]  # State awareness!
    push_ui_message("card", {...}, message=message)
```

**Frontend Pattern Migration**:
```tsx
// R014 Pattern (WebSocket + descriptor-based):
<WebSocketComponent onMessage={(descriptor) => renderWidget(descriptor)} />

// LangGraph Pattern (server-driven):
const { thread, values } = useStream({
  apiUrl: "http://localhost:2024",
  assistantId: "agent",
  onCustomEvent: (event, options) => {
    options.mutate((prev) => {
      const ui = uiMessageReducer(prev.ui ?? [], event);
      return { ...prev, ui };
    });
  },
});

{values.ui?.map((ui) => (
  <LoadExternalComponent key={ui.id} stream={thread} message={ui} />
))}
```

---

## 4. Tradeoff Analysis

### 4.1 Approach A: Single Monolithic Agent

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐⭐ | Single file, easier to understand initially |
| Performance | ⭐⭐⭐ | No IPC overhead |
| Maintainability | ⭐ | Violates SRP; hard to test; large files |
| Testability | ⭐⭐ | Hard to isolate components |
| Flexibility | ⭐ | Adding features requires touching core logic |

**Pros**:
- Simpler initial setup
- No inter-process communication
- Faster to implement prototype

**Cons**:
- Violates Single Responsibility Principle
- Hard to test individual components
- File size exceeds 150-line limit
- UI and RAG logic tightly coupled
- Difficult to swap implementations

### 4.2 Approach B: Conference Room Pattern (Specialists)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐ | Multiple files; requires orchestration |
| Performance | ⭐⭐⭐ | Minimal overhead (same process) |
| Maintainability | ⭐⭐⭐ | Clear separation; easy to modify specialists |
| Testability | ⭐⭐⭐ | Each agent tested independently |
| Flexibility | ⭐⭐⭐ | Easy to add/remove specialists |

**Pros**:
- Clear separation of concerns
- Each agent under 150 lines
- Easy to test in isolation
- Can swap specialist implementations
- Follows LLD definitions exactly

**Cons**:
- More files to manage
- Requires orchestration logic
- Slightly more initial setup

### 4.3 Decision: Conference Room Pattern (Approach B)

**Rationale**: The maintainability and testability benefits far outweigh the slight increase in complexity. The LLD explicitly defines the conference room pattern with MainDSPyReActAgent as CEO orchestrating UIDSPyAgent and RAGDSPyAgent specialists. This approach also keeps file sizes within policy limits.

---

## 5. Implementation Details

### 5.1 Key Classes/Modules

| Module | Responsibility | Dependencies | Lines (est.) |
|--------|----------------|--------------|--------------|
| `MainDSPyReActAgent` | CEO orchestrator with multi-signature pattern | DSPy, Tool*, Signature* | ~120 |
| `UIDSPyAgent` | UI specialist for descriptor generation | DSPy, C002 descriptors | ~80 |
| `RAGDSPyAgent` | RAG specialist for context retrieval | DSPy, MemoryRepository | ~80 |
| `BackendLangGraphState` | TypedDict for agent reasoning state | LangGraph, AgentStatus | ~50 |
| `FrontendLangGraphState` | TypedDict for UI lifecycle state | LangGraph, VisibilityState | ~50 |
| `AgentOrchestrator` | Coordinates state machines + agents | LangGraph, DSPy agents | ~120 |
| `ExecuteAgentQueryUseCase` | Non-streaming query execution | AgentOrchestrator, DTOs | ~80 |
| `StreamUIUpdateUseCase` | Streaming query execution | dspy.streamify, WebSocket | ~80 |

### 5.2 Port Assignments

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| **LangGraph Server** | **2024** | **HTTP/WS** | **Main agent server (LangGraph default)** |
| Frontend Dev | 3000 | HTTP | Next.js dev server |
| Voice API | 8015 | HTTP | Audio streaming (C004) |
| Search API | 8016 | HTTP | Web search service (C005) |

**Port Selection Rationale**:
- **2024**: LangGraph default port (avoids 8000-8014 range per constraints)
- **3000**: Next.js default dev server
- **8015-8016**: Voice and search services (C004, C005)

**Note**: LangGraph server handles both REST and WebSocket via SDK on port 2024.

### 5.3 Storage Schema

**Redis (Active Sessions)**:
```python
# Key pattern: session:{session_id}
{
    "session_id": "uuid",
    "user_id": "sha256_hash",
    "state": "active",
    "created_at": "2026-01-28T10:00:00Z",
    "modified_at": "2026-01-28T10:05:00Z",
    "last_activity_at": "2026-01-28T10:05:00Z",
    "conversation_history": '[{"role": "user", "content": "..."}]',
    "current_reasoning_step": 3,
    "total_tool_calls": 5
}
# TTL: 24 hours (extends on activity)
```

**Qdrant (Tier 2 Memory - Session)**:
```python
# Collection: session_memory_{session_id}
{
    "vector": [0.1, 0.2, ...],  # Embedding
    "payload": {
        "content": "User prefers Italian food",
        "timestamp": "2026-01-28T10:00:00Z",
        "source": "conversation"
    }
}
# TTL: 7 days (session-scoped)
```

**Mem0AI (Tier 3 Memory - Long-term)**:
```python
# Managed by Mem0AI
{
    "memory": "User prefers Italian food, especially pasta carbonara",
    "metadata": {
        "user_id": "sha256_hash",
        "category": "preference",
        "created_at": "2026-01-28T10:00:00Z"
    }
}
# TTL: Indefinite (consolidated memories)
```

### 5.4 DSPy Configuration

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Ollama LM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "ollama_chat/gemma3:4b"

    # DSPy
    dspy_max_iters: int = 8
    dspy_confidence_threshold: float = 0.7

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Mem0AI
    mem0_enabled: bool = True

    # Redis
    redis_url: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"

# core/dependencies.py
import dspy
from core.config import get_settings

def get_lm() -> dspy.LM:
    settings = get_settings()
    return dspy.LM(
        settings.ollama_model,
        api_base=settings.ollama_base_url,
        api_key=""
    )

def configure_dspy():
    lm = get_lm()
    dspy.configure(lm=lm)
```

---

## 6. Security Considerations

| Concern | Mitigation |
|---------|------------|
| **Tool injection** | Wrap all tools with `dspy.Tool()` to prevent LLM from inventing tools |
| **PII in memories** | Hash user_id with SHA-256; redact PII before storage |
| **Query injection** | Validate and sanitize all user inputs; use Pydantic models |
| **Session hijacking** | Use UUID for session_id; validate session ownership on each request |
| **Memory isolation** | Enforce user_id in all memory operations; never cross user boundaries |
| **DoS via long queries** | Enforce max_iters=8; add timeout per query (30s) |
| **WebSocket abuse** | Rate limit connections; enforce session ownership |
| **RAG hallucination** | Agentic RAG with quality scoring; only inject high-confidence context |

---

## 7. Performance Considerations

| Concern | Mitigation |
|---------|------------|
| **LLM latency** | Use streaming (dspy.streamify) for perceived responsiveness |
| **Memory retrieval** | Limit to 10 memories; use Qdrant HNSW index for fast search |
| **State machine overhead** | LangGraph compiled graphs are efficient (~1ms per transition) |
| **WebSocket backpressure** | Implement queue with max size; drop old messages if queue full |
| **Session storage** | Redis for active sessions (in-memory, fast) |
| **Concurrent queries** | Async/await throughout; no blocking calls |
| **Cold start** | Warmup LM on startup; pre-load common embeddings |
| **Tool execution time** | Add timeout to all tool calls (5s default) |

---

**Next Artifact**: tasks.md
