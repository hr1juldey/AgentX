# AGENTX Incremental Release Plan LLD

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Locked
**Dependencies**: All LLD documents

---

## Table of Contents

1. [Release Strategy](#1-release-strategy)
2. [Phase Definitions](#2-phase-definitions)
3. [Phase Details](#3-phase-details)
4. [Verification Criteria](#4-verification-criteria)
5. [Dependency Map](#5-dependency-map)

---

## 1. Release Strategy

### 1.1 Incremental Delivery Principles

**Each Phase Must**:
- Be usable/releasable after completion
- Take 2-3 hours to implement
- Build on previous phases
- Have frozen APIs (no breaking changes)
- Have verification criteria

**API Freezing Rules**:
- Once a phase is complete, its APIs are frozen
- Subsequent phases must use existing APIs
- Breaking changes require new major version

### 1.2 Phase Overview

| Phase | Duration | Focus | Deliverables | APIs Frozen |
|-------|----------|-------|--------------|-------------|
| **Phase 0** | 2-3 hours | Server Setup | FastAPI, Config, DI | Settings structure |
| **Phase 1** | 2-3 hours | Domain + Infrastructure | Entities, Repositories, Adapters | Entity structures |
| **Phase 2** | 2-3 hours | Main Agent | DSPy ReAct, Tools | Agent signature |
| **Phase 3** | 2-3 hours | UI + Streaming | UI Agent, Descriptors, WebSocket | Descriptor schemas |
| **Phase 4** | 2-3 hours | State Machines | LangGraph nodes, transitions | State schemas |
| **Phase 5** | 2-3 hours | Memory + RAG | Mem0AI, RAG Agent, Consolidation | RAG interface |
| **Phase 6** | 2-3 hours | Plugins | Plugin interface, Permissions | Plugin protocol |
| **Phase 7** | 2-3 hours | Hardening | Tests, Error handling, Monitoring | Complete system |

---

## 2. Phase Definitions

### Phase 0: Minimal System (2-3 hours)

**Implemented**:
- FastAPI server with health endpoint
- Pydantic Settings with .env support
- Dependency injection container
- Basic file structure (Clean Architecture layers)
- CORS and logging middleware

**Stubbed**:
- All repositories (raise NotImplementedError)
- All agents (return mock responses)
- WebSocket endpoints (return 501 Not Implemented)

**Frozen APIs**:
- `core/config.Settings`
- `core/dependencies.get_settings()`
- `core/dependencies.get_*_repository()`
- Main application factory

**Verification**:
```bash
# Health check returns 200
curl http://localhost:8000/health

# Settings loaded from .env
curl http://localhost:8000/api/v1/config
```

---

### Phase 1: Domain + Infrastructure (2-3 hours)

**Implemented**:
- All entities: `AgentSessionEntity`, `UIComponentEntity`, `MemoryConsolidationEntity`
- All enums: `SessionState`, `UIComponentType`, etc.
- Repository interfaces: `AgentSessionRepository`, `UIComponentRepository`, `MemoryRepository`
- Qdrant adapter (Tier 2 memory)
- Redis session adapter (active sessions)
- SQLite session adapter (long-term sessions)
- In-memory UI component repository

**Stubbed**:
- Agent logic
- UI descriptors
- WebSocket streaming

**Frozen APIs**:
- All entity classes (names, fields, methods)
- All repository interfaces (method signatures)
- All enums (values locked)

**Verification**:
```python
# Test entity creation
session = AgentSessionEntity(
    session_id=uuid4(),
    user_id="test_hash",
    state=SessionState.INITIALIZING,
    created_at=datetime.utcnow(),
    modified_at=datetime.utcnow(),
    last_activity_at=datetime.utcnow()
)
assert session.is_active() == False

# Test repository CRUD
created = await redis_repo.create(session)
retrieved = await redis_repo.get_by_id(session.session_id)
assert retrieved.session_id == session.session_id
```

---

### Phase 2: Main DSPy Agent (2-3 hours)

**Implemented**:
- `MainDSPyReActAgent` with multi-signature pattern
- Basic tools: `safe_calculator`, `searxng_search`, `get_current_weather`
- `ToolSelectionSignature`, `ConfidenceScoringSignature`
- `ExecuteAgentQueryUseCase` (without streaming)
- Command/Query DTOs

**Stubbed**:
- UI agent (return empty UI updates)
- RAG agent (return empty context)
- LangGraph state machines
- WebSocket streaming

**Frozen APIs**:
- `MainDSPyReActAgent` (class name, method signatures)
- `MainAgentSignature`, `ToolSelectionSignature`, `ConfidenceScoringSignature`
- Tool function signatures
- `ExecuteAgentQueryCommand`, `ExecuteAgentQueryResponse`

**Verification**:
```python
# Test agent with calculator
lm = dspy.LM("ollama_chat/gemma3:4b")
dspy.configure(lm=lm)

tools = [dspy.Tool(safe_calculator)]
agent = MainDSPyReActAgent(tools=tools, max_iters=3)

result = agent(
    user_query="What is 2 + 2?",
    conversation_history=[],
    retrieved_context=""
)

assert "4" in result.final_answer
assert result.confidence_score > 0.0
```

---

### Phase 3: UI DSPy Agent + Descriptors (2-3 hours)

**Implemented**:
- All 7 core UI descriptors (Pydantic models)
- `UIDSPyAgent` with 6 signatures
- `UIService` for descriptor creation
- WebSocket manager with streaming
- All WebSocket message types
- `StreamUIUpdateUseCase`

**Stubbed**:
- LangGraph state machines
- Form interrupt/resume
- Progress indicator lifecycle

**Frozen APIs**:
- All descriptor classes (7 types locked)
- `UIDescriptorType` enum (closed set)
- `WebSocketMessageType` enum
- `UIDSPyAgent` signatures
- `WebSocketManager` methods

**Verification**:
```python
# Test descriptor creation
card = CardDescriptor(
    descriptor_id=str(uuid4()),
    title="Test Card",
    content="Test content",
    actions=[]
)
assert card.descriptor_type == UIDescriptorType.CARD

# Test WebSocket message
msg = WebSocketMessage(
    message_type=WebSocketMessageType.DESCRIPTOR_CREATE,
    session_id=str(uuid4()),
    data={"descriptor": card.model_dump()}
)
assert msg.message_type == "descriptor_create"
```

---

### Phase 4: LangGraph State Machines (2-3 hours)

**Implemented**:
- `BackendLangGraphState` (TypedDict)
- `FrontendLangGraphState` (TypedDict)
- Backend state machine nodes (start, execute_step, complete, error)
- Frontend state machine nodes (create, update, dismiss, form_submit)
- State transition logic
- Form interrupt/resume
- `AgentOrchestrator` for state machine coordination

**Stubbed**:
- Memory consolidation
- Plugin system
- Multi-agent coordination (UI agent, RAG agent)

**Frozen APIs**:
- `BackendLangGraphState`, `FrontendLangGraphState` schemas
- State machine node function signatures
- State transition rules

**Verification**:
```python
# Test backend state machine
workflow = create_backend_state_machine()
state = {
    "session_id": str(uuid4()),
    "user_query": "Test query",
    "agent_status": AgentStatus.IDLE,
    "should_continue": True
}

result = await workflow.ainvoke(state)
assert result["agent_status"] == AgentStatus.COMPLETED
```

---

### Phase 5: Memory + RAG (2-3 hours)

**Implemented**:
- `RAGDSPyAgent` with retrieval and injection signatures
- Mem0AI adapter implementation
- Three-tier memory architecture (Tier 1, 2, 3)
- Memory consolidation service
- Context retrieval with confidence scoring
- Agentic RAG pattern (not simple dump)

**Stubbed**:
- Plugin system
- UI plugin extensions

**Frozen APIs**:
- `RAGDSPyAgent` (class name, methods)
- `RetrievalSignature`, `ContextInjectionSignature`
- Three-tier memory interface
- Consolidation trigger logic

**Verification**:
```python
# Test memory storage
memory_id = await qdrant_repo.store_memory(
    content="Test memory",
    user_id="test_user",
    metadata={"source": "test"}
)
assert isinstance(memory_id, UUID)

# Test memory retrieval
results = await qdrant_repo.search_memories(
    query="test",
    user_id="test_user",
    limit=5
)
assert len(results) > 0
```

---

### Phase 6: Plugin System (2-3 hours)

**Implemented**:
- `AgentXPlugin` abstract base class
- `PluginPermissions` with all permission types
- `PluginManifest` with validation
- `PluginRegistry` for lifecycle management
- Permission enforcement checks
- Code signing verification
- Resource quota enforcement

**Stubbed**:
- External plugins (use mock plugins for testing)
- Plugin UI descriptor extensions (prepare protocol)

**Frozen APIs**:
- `AgentXPlugin` (all abstract methods)
- `PluginPermissions` (all fields locked)
- `PluginManifest` (schema locked)
- `PluginRegistry` (public methods)

**Verification**:
```python
# Test plugin lifecycle
plugin = MockPlugin()
await registry.install_plugin(plugin)
assert registry.is_enabled(plugin.plugin_id) == False

await registry.enable_plugin(plugin.plugin_id)
assert registry.is_enabled(plugin.plugin_id) == True

# Test permission enforcement
plugin.permissions = PluginPermissions(allow_network_access=False)
with pytest.raises(PermissionError):
    await safe_plugin_operation(plugin, "network", host="example.com")
```

---

### Phase 7: Production Hardening (2-3 hours)

**Implemented**:
- All stubbed items from Phases 0-6
- Error handling with try/except/finally
- Logging with structured logs
- Health check endpoints for all components
- Metrics collection (tool calls, latency, errors)
- Rate limiting per user
- Input validation on all endpoints
- PII redaction at all entry points
- Unit tests (70% coverage target)
- Integration tests (real DSPy + Ollama)
- E2E tests (complete flows)

**Frozen APIs**:
- Complete system (all components)

**Verification**:
```bash
# Run all tests
pytest tests/ --cov=agentx --cov-report=html

# Health check all components
curl http://localhost:8000/health
# Returns: {"status": "healthy", "components": {...}}

# Load test
ab -n 1000 -c 10 http://localhost:8000/api/v1/agent/query
# Should handle 100 concurrent connections
```

---

## 3. Phase Details

### 3.1 Phase 0 Detailed Tasks

**File Structure**:
```
agentx/
├── core/
│   ├── config.py (45 lines)
│   └── dependencies.py (30 lines)
├── main.py (20 lines)
└── .env.example (15 lines)
```

**Tasks**:
1. Create `core/config.py` with Pydantic Settings
2. Create `core/dependencies.py` with dependency injection
3. Create `main.py` with FastAPI factory
4. Add health endpoint at `/health`
5. Add CORS middleware
6. Add request logging middleware
7. Create `.env.example` template

**Lines of Code**: ~150 lines

### 3.2 Phase 1 Detailed Tasks

**File Structure**:
```
agentx/
├── domain/
│   ├── entities/
│   │   ├── agent_session.py (70 lines)
│   │   ├── ui_component.py (60 lines)
│   │   └── enums.py (40 lines)
│   └── repositories/
│       ├── agent_session_repository.py (40 lines)
│       └── memory_repository.py (50 lines)
├── infrastructure/
│   ├── database/
│   │   ├── redis_session_adapter.py (80 lines)
│   │   └── sqlite_session_adapter.py (90 lines)
│   └── external/
│       └── qdrant_vector_store.py (120 lines)
```

**Tasks**:
1. Create all entity classes with business methods
2. Create all enums (locked values)
3. Create repository interfaces (ABC)
4. Implement Redis adapter
5. Implement SQLite adapter
6. Implement Qdrant adapter
7. Add unit tests for entities

**Lines of Code**: ~650 lines

### 3.3 Phase 2 Detailed Tasks

**File Structure**:
```
agentx/
├── agent/
│   ├── dspy_signatures/
│   │   └── main_signatures.py (50 lines)
│   ├── tools/
│   │   └── main_tools.py (100 lines)
│   └── dspy_agents/
│       └── main_react_agent.py (120 lines)
├── application/
│   ├── use_cases/
│   │   └── execute_agent_query.py (80 lines)
│   ├── commands/
│   │   └── agent_commands.py (30 lines)
│   └── dtos/
│       └── agent_dtos.py (80 lines)
```

**Tasks**:
1. Create DSPy signatures
2. Create tools (calculator, search, weather)
3. Create MainDSPyReActAgent
4. Create ExecuteAgentQueryUseCase
5. Create command/response DTOs
6. Add integration tests (real Ollama)

**Lines of Code**: ~540 lines

### 3.4 Phase 3 Detailed Tasks

**File Structure**:
```
agentx/
├── ui/
│   ├── descriptors/
│   │   ├── base.py (40 lines)
│   │   ├── markdown_block.py (30 lines)
│   │   ├── card.py (50 lines)
│   │   ├── form.py (100 lines)
│   │   ├── progress.py (40 lines)
│   │   ├── action.py (30 lines)
│   │   ├── confirmation.py (50 lines)
│   │   └── voice.py (40 lines)
│   └── protocols/
│       └── websocket_messages.py (150 lines)
├── agent/
│   ├── dspy_signatures/
│   │   └── ui_signatures.py (80 lines)
│   ├── dspy_agents/
│   │   └── ui_agent.py (80 lines)
│   └── tools/
│       └── ui_tools.py (80 lines)
├── application/
│   ├── use_cases/
│   │   └── stream_ui_update.py (40 lines)
│   └── dtos/
│       └── ui_dtos.py (60 lines)
└── infrastructure/
    └── external/
        └── websocket_manager.py (100 lines)
```

**Tasks**:
1. Create all 7 UI descriptors
2. Create WebSocket message types
3. Create UIDSPyAgent with 6 signatures
4. Create UI tools
5. Create WebSocket manager
6. Create StreamUIUpdateUseCase
7. Add WebSocket endpoint

**Lines of Code**: ~1100 lines

### 3.5 Phase 4 Detailed Tasks

**File Structure**:
```
agentx/
├── agent/
│   └── langgraph/
│       ├── backend_state_machine.py (150 lines)
│       └── frontend_state_machine.py (150 lines)
├── application/
│   └── services/
│       ├── agent_orchestrator.py (120 lines)
│       └── ui_service.py (150 lines)
└── presentation/
    └── api/
        └── v1/
            └── agent_routes.py (100 lines)
```

**Tasks**:
1. Create backend state machine with nodes
2. Create frontend state machine with nodes
3. Create state transition logic
4. Create AgentOrchestrator
5. Create UIService with form interrupt
6. Add form submit endpoint
7. Add state management endpoints

**Lines of Code**: ~770 lines

### 3.6 Phase 5 Detailed Tasks

**File Structure**:
```
agentx/
├── agent/
│   ├── dspy_signatures/
│   │   └── rag_signatures.py (60 lines)
│   └── dspy_agents/
│       └── rag_agent.py (120 lines)
├── infrastructure/
│   └── external/
│       └── mem0_memory.py (80 lines)
├── application/
│   └── services/
│       └── memory_service.py (150 lines)
└── tests/
    └── integration/
        └── test_rag.py (100 lines)
```

**Tasks**:
1. Create RAG signatures
2. Create RAGDSPyAgent
3. Implement Mem0AI adapter
4. Create MemoryService with consolidation
5. Implement three-tier memory
6. Add memory endpoints
7. Add integration tests (real Qdrant + Mem0AI)

**Lines of Code**: ~610 lines

### 3.7 Phase 6 Detailed Tasks

**File Structure**:
```
agentx/
├── plugin/
│   ├── interface.py (150 lines)
│   ├── permissions.py (120 lines)
│   ├── manifest.py (100 lines)
│   ├── registry.py (200 lines)
│   └── types.py (40 lines)
├── presentation/
│   └── api/
│       └── v1/
│           └── plugin_routes.py (150 lines)
└── tests/
    ├── unit/
    │   └── plugin/
    │       └── test_permissions.py (80 lines)
    └── integration/
        └── test_plugin_lifecycle.py (100 lines)
```

**Tasks**:
1. Create AgentXPlugin ABC
2. Create PluginPermissions with presets
3. Create PluginManifest with validation
4. Create PluginRegistry with lifecycle
5. Add code signing verification
6. Add resource quota enforcement
7. Add plugin management endpoints
8. Create mock plugin for testing

**Lines of Code**: ~940 lines

### 3.8 Phase 7 Detailed Tasks

**File Structure**:
```
agentx/
├── core/
│   └── middleware/
│       ├── error_handler.py (80 lines)
│       └── rate_limit.py (60 lines)
├── tests/
│   ├── unit/ (2000 lines total)
│   ├── integration/ (1000 lines total)
│   └── e2e/ (500 lines total)
├── monitoring/
│   ├── metrics.py (100 lines)
│   └── health.py (80 lines)
└── scripts/
    └── setup.sh (50 lines)
```

**Tasks**:
1. Complete all stubbed implementations
2. Add error handling with try/except
3. Add structured logging
4. Add rate limiting
5. Add metrics collection
6. Add comprehensive tests
7. Add health checks for all components
8. Add PII redaction
9. Performance optimization
10. Documentation

**Lines of Code**: ~3870 lines (including tests)

---

## 4. Verification Criteria

### 4.1 Per-Phase Checklist

**Phase 0**:
- [ ] Health endpoint returns 200
- [ ] Settings loaded from .env
- [ ] CORS enabled
- [ ] Logging working

**Phase 1**:
- [ ] Entity unit tests pass
- [ ] Repository CRUD tests pass
- [ ] Qdrant stores and retrieves vectors
- [ ] Redis stores and retrieves sessions
- [ ] SQLite persists sessions

**Phase 2**:
- [ ] Agent executes query successfully
- [ ] Calculator tool works
- [ ] Search tool works
- [ ] Confidence score calculated
- [ ] Tool calls recorded

**Phase 3**:
- [ ] All 7 descriptors validate
- [ ] WebSocket connects and streams
- [ ] UI agent generates descriptors
- [ ] Messages follow protocol

**Phase 4**:
- [ ] Backend state machine transitions
- [ ] Frontend state machine transitions
- [ ] Form interrupt works
- [ ] Form resume works

**Phase 5**:
- [ ] RAG retrieves memories
- [ ] Context injection decision works
- [ ] Consolidation runs
- [ ] Three-tier memory works

**Phase 6**:
- [ ] Plugin installs
- [ ] Plugin enables/disables
- [ ] Permissions enforced
- [ ] Code signature verified
- [ ] Resource quotas enforced

**Phase 7**:
- [ ] All unit tests pass (70% coverage)
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Error handling works
- [ ] Rate limiting works
- [ ] Health checks pass

### 4.2 Cumulative Metrics

| Phase | Lines of Code | Files | Tests | Coverage |
|-------|---------------|-------|-------|----------|
| Phase 0 | 150 | 4 | 0 | 0% |
| Phase 1 | 800 | 15 | 50 | 60% |
| Phase 2 | 1340 | 25 | 150 | 65% |
| Phase 3 | 2440 | 40 | 300 | 60% |
| Phase 4 | 3210 | 48 | 400 | 62% |
| Phase 5 | 3820 | 55 | 550 | 65% |
| Phase 6 | 4760 | 65 | 700 | 68% |
| Phase 7 | 8630 | 100 | 3500 | 70% |

**Total**: ~8600 lines of code, 100 files, 3500 tests

---

## 5. Dependency Map

### 5.1 Phase Dependencies

```
Phase 0 (Foundation)
    ↓
Phase 1 (Domain + Infrastructure)
    ↓
Phase 2 (Main Agent)
    ↓
Phase 3 (UI + Streaming)
    ↓
Phase 4 (State Machines)
    ↓
Phase 5 (Memory + RAG)
    ↓
Phase 6 (Plugins)
    ↓
Phase 7 (Hardening)
```

### 5.2 Critical Path

**Must Complete In Order**:
1. Phase 0 → Phase 1 (entities required for everything)
2. Phase 2 → Phase 3 (UI agent depends on main agent)
3. Phase 3 → Phase 4 (state machines depend on UI)
4. Phase 4 → Phase 5 (memory integration after state)
5. Phase 5 → Phase 6 (plugins depend on memory)

**Can Parallelize**:
- Phase 3 (UI) + Phase 5 (Memory) - independent
- Phase 4 (State) + Phase 6 (Plugins) - independent

---

**This incremental release plan is part of AGENTX LLD v1.0. All phases and timelines are locked.**
