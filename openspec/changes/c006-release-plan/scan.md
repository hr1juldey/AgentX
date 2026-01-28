# Scan Artifact: c006-release-plan

**Generated**: 2026-01-28
**Change**: c006-release-plan
**Schema**: spec-factory v1

---

## 1. LLD Synthesis

### 1.1 Relevant LLD Documents

| Document | Path | Relevance |
|----------|------|-----------|
| Incremental Release Plan LLD | `docs/engineering/lld/incremental_release_plan.md` | **PRIMARY** - 8-phase implementation plan (LOCKED) |
| Domain Model LLD | `docs/engineering/lld/domain_model.md` | **PRIMARY** - Entity definitions, enums, repository interfaces (LOCKED) |
| Agent Runtime LLD | `docs/engineering/lld/agent_runtime.md` | **SECONDARY** - DSPy agent signatures, LangGraph definitions |
| Infrastructure Adapters LLD | `docs/engineering/lld/infrastructure_adapters.md` | **SECONDARY** - WebSocket, Ollama adapters |

### 1.2 Locked Definitions from LLD

**8-Phase Incremental Release Plan** (incremental_release_plan.md:36-48):

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

**Incremental Delivery Principles** (incremental_release_plan.md:22-29):

Each Phase Must:
- Be usable/releasable after completion
- Take 2-3 hours to implement
- Build on previous phases
- Have frozen APIs (no breaking changes)
- Have verification criteria

**API Freezing Rules** (incremental_release_plan.md:31-34):
- Once a phase is complete, its APIs are frozen
- Subsequent phases must use existing APIs
- Breaking changes require new major version

### 1.3 Change Dependencies (C001-C005)

The incremental release plan requires all previous changes to be complete:

| Change | Status | Required For Phases |
|--------|--------|---------------------|
| **C001-folder-structure** | Complete | All phases (Clean Architecture layers) |
| **C002-data-contracts** | Complete | Phase 2+ (Pydantic DTOs) |
| **C003-agent-pipeline** | Complete | Phase 2-4 (DSPy agents, LangGraph) |
| **C004-voice-streaming** | Complete | Phase 7+ (voice integration) |
| **C005-memory-rag** | Complete | Phase 5 (Memory + RAG) |

---

## 2. Codebase Exploration (opsx:explore)

### 2.1 Exploration Topics

```
Forced Topics:
1. Incremental release strategy (8-phase plan)
2. API freezing rules (breaking changes, versioning)
3. Verification criteria (health checks, tests)
4. Dependency ordering (what depends on what)
5. Integration points between phases
```

### 2.2 File Inventory

#### OpenSpec Changes (Specifications)

| Change | Artifacts | Purpose |
|--------|-----------|---------|
| C001-folder-structure | 7 artifacts | Clean Architecture file organization |
| C002-data-contracts | 7 artifacts | Pydantic v2 ↔ Zod alignment |
| C003-agent-pipeline | 7 artifacts | DSPy agents, LangGraph state machines |
| C004-voice-streaming | 7 artifacts | VAD, STT, TTS services |
| C005-memory-rag | 7 artifacts | Temporal RAG, consolidation |

#### LLD Documents (Reference)

| Document | Lines | Purpose |
|----------|-------|---------|
| `incremental_release_plan.md` | 600+ | 8-phase implementation plan (LOCKED) |
| `domain_model.md` | 700+ | Entity definitions, enums, repositories (LOCKED) |
| `agent_runtime.md` | 800+ | DSPy signatures, agents, LangGraph (LOCKED) |

---

## 3. Patterns Discovered

### 3.1 Architectural Patterns

**Incremental Build Pattern**:
```
Phase 0 (Server) → Phase 1 (Domain) → Phase 2 (Main Agent) → Phase 3 (UI) → Phase 4 (State) → Phase 5 (Memory) → Phase 6 (Plugins) → Phase 7 (Hardening)
```

**API Freezing Pattern**:
- Each phase freezes its APIs upon completion
- Subsequent phases MUST use existing frozen APIs
- Breaking changes require new major version
- Enables parallel development (multiple teams working on different phases)

**Dependency Ordering**:
- Phase 0: Independent (base server)
- Phase 1: Depends on Phase 0 (requires server)
- Phase 2: Depends on Phase 1 (requires entities)
- Phase 3: Depends on Phase 2 (requires agent)
- Phase 4: Depends on Phase 2+3 (requires agent + UI)
- Phase 5: Depends on Phase 2 (requires entities)
- Phase 6: Independent (plugin system)
- Phase 7: Depends on ALL previous phases

### 3.2 Code Patterns

**Phase Completion Criteria**:
```python
# Each phase must:
1. Implement all "Implemented" items
2. Stub all "Stubbed" items with NotImplementedError
3. Freeze all "Frozen APIs"
4. Pass verification criteria
5. Take 2-3 hours to implement
```

**Verification Pattern**:
```bash
# Each phase has verification steps:
- Health check returns 200
- Unit tests pass
- Integration tests pass
- API documentation updated
```

### 3.3 Anti-Patterns to Avoid

| Anti-Pattern | Why Avoid | Alternative |
|--------------|-----------|-------------|
| **Skipping phases** | Breaks incremental delivery | Follow 0→1→2→3→4→5→6→7 order |
| **Changing frozen APIs** | Breaks dependent phases | Use new version for breaking changes |
| **Implementing too much** | Violates 2-3 hour target | Stick to phase scope |
| **Not stubbing properly** | Confusing what's implemented | Use NotImplementedError clearly |
| **No verification** | Can't validate phase completion | Add verification criteria for each phase |

---

## 4. Reference Analysis

### 4.1 Phase 0: Minimal System

**Deliverables** (incremental_release_plan.md:53-66):
- FastAPI server with health endpoint
- Pydantic Settings with .env support
- Dependency injection container
- Basic file structure (Clean Architecture layers)
- CORS and logging middleware

**Frozen APIs**:
- `core/config.Settings`
- `core/dependencies.get_settings()`
- Main application factory

**Verification**:
```bash
curl http://localhost:8000/health  # Returns 200
```

### 4.2 Phase 1: Domain + Infrastructure

**Deliverables** (incremental_release_plan.md:84-99):
- All entities: `AgentSessionEntity`, `UIComponentEntity`, `MemoryConsolidationEntity`
- All enums: `SessionState`, `UIComponentType`, etc.
- Repository interfaces: `AgentSessionRepository`, `UIComponentRepository`, `MemoryRepository`
- Qdrant adapter, Redis session adapter, SQLite session adapter
- In-memory UI component repository

**Frozen APIs**:
- All entity classes (names, fields, methods)
- All repository interfaces (method signatures)
- All enums (values locked)

### 4.3 Phase 2: Main DSPy Agent

**Deliverables** (incremental_release_plan.md:126-141):
- `MainDSPyReActAgent` with multi-signature pattern
- Basic tools: `safe_calculator`, `searxng_search`, `get_current_weather`
- `ToolSelectionSignature`, `ConfidenceScoringSignature`
- `ExecuteAgentQueryUseCase` (without streaming)

### 4.4 Phase 3: UI DSPy Agent + Descriptors

**Deliverables** (incremental_release_plan.md:168-179):
- All 7 core UI descriptors (Pydantic models)
- `UIDSPyAgent` with 6 signatures
- `UIService` for descriptor creation
- WebSocket manager with streaming
- All WebSocket message types

### 4.5 Phase 4: LangGraph State Machines

**Deliverables** (incremental_release_plan.md:212-227):
- `BackendLangGraphState`, `FrontendLangGraphState` (TypedDict)
- Backend state machine nodes (start, execute_step, complete, error)
- Frontend state machine nodes (create, update, dismiss, form_submit)
- `AgentOrchestrator` for state machine coordination

### 4.6 Phase 5: Memory + RAG

**Deliverables** (incremental_release_plan.md:250-260):
- `RAGDSPyAgent` with retrieval and injection signatures
- Mem0AI adapter implementation
- Three-tier memory architecture
- Memory consolidation service
- Agentic RAG pattern

### 4.7 Phase 6: Plugin System

**Deliverables** (incremental_release_plan.md:291-302):
- `AgentXPlugin` abstract base class
- `PluginPermissions` with all permission types
- `PluginManifest` with validation
- `PluginRegistry` for lifecycle management
- Permission enforcement checks
- Code signing verification

### 4.8 Phase 7: Production Hardening

**Deliverables** (incremental_release_plan.md:330-344):
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

---

## 5. Key Files for This Change

```
# LLD Documents (PRIMARY)
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/incremental_release_plan.md

# LLD Documents (SECONDARY)
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/domain_model.md
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/agent_runtime.md
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/infrastructure_adapters.md

# Completed OpenSpec Changes
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c001-folder-structure/
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c002-data-contracts/
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c003-agent-pipeline/
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c004-voice-streaming/
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c005-memory-rag/
```

---

**Next Artifact**: extract.md
