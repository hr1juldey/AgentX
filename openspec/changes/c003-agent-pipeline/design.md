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

### 1.2 Layer Structure (Clean Architecture)

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
├── agent/                          # DSPy agents (domain + infrastructure)
│   ├── dspy_signatures/
│   │   ├── main_signatures.py      # MainAgentSignature, ToolSelectionSignature, ConfidenceScoringSignature
│   │   ├── ui_signatures.py        # SelectWidgetSignature, ConfigureFormSignature, etc.
│   │   └── rag_signatures.py       # RetrievalSignature, ContextInjectionSignature
│   ├── tools/
│   │   ├── main_tools.py           # safe_calculator, searxng_search, get_current_weather
│   │   └── ui_tools.py             # render_markdown_block, render_card, etc.
│   ├── dspy_agents/
│   │   ├── main_react_agent.py     # MainDSPyReActAgent (CEO orchestrator)
│   │   ├── ui_agent.py             # UIDSPyAgent (UI specialist)
│   │   └── rag_agent.py            # RAGDSPyAgent (RAG specialist)
│   └── langgraph/
│       ├── backend_state_machine.py    # BackendLangGraphState, workflow
│       └── frontend_state_machine.py   # FrontendLangGraphState, workflow
│
├── application/                    # Use case orchestration
│   ├── use_cases/
│   │   ├── execute_agent_query.py  # ExecuteAgentQueryUseCase
│   │   └── stream_ui_update.py     # StreamUIUpdateUseCase
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
│       └── websocket_manager.py    # WebSocketManager
│
└── presentation/                   # FastAPI routes
    └── api/
        └── v1/
            ├── agent_routes.py    # /api/v1/agent/query, /api/v1/agent/stream
            └── session_routes.py  # /api/v1/session/*
```

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

### 2.2 Agent Query Flow (Streaming)

```
┌─────────┐    POST /api/v1/agent/stream   ┌──────────────┐
│ Client  │────────────────────────────────▶│ FastAPI      │
└────┬────┘                                   │ Route        │
     │                                         └──────┬───────┘
     │ WebSocket Upgrade                             │
     │                                                │
┌────▼─────────────────────────────────────────────▼─────────┐
│                 WebSocket Connection Established           │
└────┬───────────────────────────────────────────────┬───────┘
     │                                               │
     │         StreamUIUpdateUseCase.execute()      │
     │                                               │
     │  1. Warmup: agent.forward("warmup", ...)    │
     │  2. Wrap: stream_agent = dspy.streamify()   │
     │  3. Async iterate:                           │
     │     ┌─→ TOKEN message (LLM token)            │
     │     ├─→ REASONING_STEP message              │
     │     ├─→ TOOL_CALL message                   │
     │     └─→ DESCRIPTOR_CREATE message           │
     │                                               │
     │  4. Return final ExecuteAgentQueryResponse  │
     │                                               │
┌────▼─────────────────────────────────────────────▼─────────┐
│                    Frontend Processes Stream                │
│                                                              │
│  • TOKEN → Append to chat message                           │
│  • REASONING_STEP → Display in reasoning panel              │
│  • TOOL_CALL → Display tool call status                     │
│  • DESCRIPTOR_CREATE → Render UI component                  │
└──────────────────────────────────────────────────────────────┘
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
| **State Management** | LangGraph TypedDict state machines | Manual state tracking | Declarative; visualizable; built-in error handling |
| **RAG Approach** | Agentic (retrieve → score → decide → filter) | Simple context dump | Better context quality; avoids injection failures |
| **Frontend Rendering** | Descriptor ID pattern (not HTML in agent) | Agent generates HTML | Separation of concerns; type-safe |
| **File Organization** | Split agents (main, ui, rag) | Single large agent file | Keeps files under 150 lines; improves maintainability |

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
| Main API | 8015 | HTTP | REST endpoints (/api/v1/agent/*, /api/v1/session/*) |
| WebSocket | 8016 | WS | WebSocket streaming (/ws/agent/{session_id}) |
| Health Check | 8017 | HTTP | Health monitoring (/health, /health/ready) |

**Port Selection Rationale**:
- Avoids 8000-8014 range (reserved for other services)
- 8015 for API (easy to remember)
- 8016 for WebSocket (API + 1)
- 8017 for Health (API + 2)

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
