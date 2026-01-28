# Design Artifact: c006-release-plan

**Generated**: 2026-01-28
**Change**: c006-release-plan
**Schema**: spec-factory v1

---

## 1. Architecture

### 1.1 Phase Dependency Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Incremental Delivery Architecture                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Phase 0 (Server Setup) ──────────────────────────────────────┐        │
│    ├─ FastAPI server                                          │        │
│    ├─ Pydantic Settings                                       │        │
│    ├─ Dependency Injection                                    │        │
│    └─ Health endpoint (/health)                               │        │
│                                                              ↓         │
│  Phase 1 (Domain + Infrastructure) ──────────────────────┐   │        │
│    ├─ All entities (@dataclass)                           │   │        │
│    ├─ Repository interfaces (ABC)                         │   │        │
│    ├─ Qdrant adapter                                      │   │        │
│    ├─ Redis session adapter                               │   │        │
│    └─ Frozen: Entity structures, Repository signatures    │   │        │
│                                                          ↓   │        │
│  Phase 2 (Main DSPy Agent) ──────────────────────────┐   │   │        │
│    ├─ MainDSPyReActAgent                              │   │   │        │
│    ├─ Basic tools (calculator, search, weather)       │   │   │        │
│    ├─ ExecuteAgentQueryUseCase                        │   │   │        │
│    └─ Frozen: Agent signature                         │   │   │        │
│                                                      ↓   │   │        │
│  Phase 3 (UI + Streaming) ──────────────────────┐   │   │   │        │
│    ├─ 7 core UI descriptors (Pydantic)          │   │   │   │        │
│    ├─ UIDSPyAgent (6 signatures)                │   │   │   │        │
│    ├─ WebSocket manager                         │   │   │   │        │
│    └─ Frozen: Descriptor schemas                │   │   │   │        │
│                                                  ↓   │   │   │        │
│  Phase 4 (State Machines) ──────────────────┐   │   │   │   │        │
│    ├─ BackendLangGraphState (TypedDict)      │   │   │   │   │        │
│    ├─ FrontendLangGraphState (TypedDict)     │   │   │   │   │        │
│    ├─ Backend state machine nodes            │   │   │   │   │        │
│    ├─ Frontend state machine nodes           │   │   │   │   │        │
│    └─ Frozen: State schemas                  │   │   │   │   │        │
│                                              ↓   │   │   │   │        │
│  Phase 5 (Memory + RAG) ────────────────┐   │   │   │   │   │        │
│    ├─ RAGDSPyAgent                        │   │   │   │   │   │        │
│    ├─ QdrantVectorStoreAdapter            │   │   │   │   │   │        │
│    ├─ Mem0MemoryAdapter                   │   │   │   │   │   │        │
│    ├─ TemporalRAGService                  │   │   │   │   │   │        │
│    └─ Frozen: RAG interface               │   │   │   │   │   │        │
│                                          ↓   │   │   │   │   │        │
│  Phase 6 (Plugins) ──────────────────┐   │   │   │   │   │   │        │
│    ├─ AgentXPlugin (ABC)              │   │   │   │   │   │   │        │
│    ├─ PluginPermissions               │   │   │   │   │   │   │        │
│    ├─ PluginManifest                  │   │   │   │   │   │   │        │
│    ├─ PluginRegistry                   │   │   │   │   │   │   │        │
│    └─ Frozen: Plugin protocol          │   │   │   │   │   │   │        │
│                                      ↓   │   │   │   │   │   │        │
│  Phase 7 (Production Hardening) ──┐   │   │   │   │   │   │   │        │
│    ├─ All stubbed items implemented│   │   │   │   │   │   │   │        │
│    ├─ Error handling (try/except)  │   │   │   │   │   │   │   │        │
│    ├─ Structured logging            │   │   │   │   │   │   │   │        │
│    ├─ Health checks (all services) │   │   │   │   │   │   │   │        │
│    ├─ Metrics collection            │   │   │   │   │   │   │   │        │
│    ├─ Rate limiting                 │   │   │   │   │   │   │   │        │
│    ├─ Input validation              │   │   │   │   │   │   │   │        │
│    ├─ PII redaction                 │   │   │   │   │   │   │   │        │
│    ├─ Unit tests (70% coverage)     │   │   │   │   │   │   │   │        │
│    └─ Frozen: Complete system       ┘   │   │   │   │   │   │   │        │
│                                          │   │   │   │   │   │        │
│                                          └───┴───┴───┴───┴───┴────────┘        │
│                                                    Depends on ALL             │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Incremental Delivery Pattern

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Incremental Build Pattern                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Start → Phase 0 (2-3h) → Verify → Freeze APIs → Release               │
│              ↓                                                         │
│         Phase 1 (2-3h) → Verify → Freeze APIs → Release                │
│              ↓                                                         │
│         Phase 2 (2-3h) → Verify → Freeze APIs → Release                │
│              ↓                                                         │
│         Phase 3 (2-3h) → Verify → Freeze APIs → Release                │
│              ↓                                                         │
│         Phase 4 (2-3h) → Verify → Freeze APIs → Release                │
│              ↓                                                         │
│         Phase 5 (2-3h) → Verify → Freeze APIs → Release                │
│              ↓                                                         │
│         Phase 6 (2-3h) → Verify → Freeze APIs → Release                │
│              ↓                                                         │
│         Phase 7 (2-3h) → Verify → Freeze APIs → Production System      │
│                                                                         │
│  Key Properties:                                                       │
│  - Each phase is usable/releasable after completion                    │
│  - APIs frozen after each phase (no breaking changes)                  │
│  - Verification criteria must pass before completion                   │
│  - Strict 2-3 hour time limit per phase                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 API Freezing Pattern

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          API Freezing Pattern                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Phase 0 Complete:                                                      │
│    ├─ core/config.Settings → FROZEN                                    │
│    ├─ core/dependencies.get_settings() → FROZEN                        │
│    └─ Main application factory → FROZEN                                │
│                                                                         │
│  Phase 1 Complete:                                                      │
│    ├─ All entity classes → FROZEN                                      │
│    ├─ All repository interfaces → FROZEN                               │
│    └─ All enums → FROZEN                                               │
│                                                                         │
│  Phase 2 Complete:                                                      │
│    ├─ MainDSPyReActAgent signature → FROZEN                            │
│    ├─ Tool interface → FROZEN                                          │
│    └─ ExecuteAgentQueryCommand → FROZEN                                │
│                                                                         │
│  Phase 3 Complete:                                                      │
│    ├─ All 7 UI descriptors → FROZEN                                    │
│    ├─ UIDSPyAgent signatures → FROZEN                                  │
│    └─ WebSocket message types → FROZEN                                 │
│                                                                         │
│  Phase 4 Complete:                                                      │
│    ├─ BackendLangGraphState → FROZEN                                   │
│    ├─ FrontendLangGraphState → FROZEN                                  │
│    └─ State machine nodes → FROZEN                                     │
│                                                                         │
│  Phase 5 Complete:                                                      │
│    ├─ RAGDSPyAgent signature → FROZEN                                  │
│    ├─ TemporalRAGService interface → FROZEN                            │
│    └─ Memory DTOs → FROZEN                                             │
│                                                                         │
│  Phase 6 Complete:                                                      │
│    ├─ AgentXPlugin interface → FROZEN                                  │
│    ├─ PluginPermissions → FROZEN                                       │
│    └─ PluginManifest → FROZEN                                          │
│                                                                         │
│  Phase 7 Complete:                                                      │
│    └─ COMPLETE SYSTEM → FROZEN (v8.0.0)                                │
│                                                                         │
│  Breaking Change Required?                                              │
│    ├─ Create new major version (v9.0.0)                                │
│    ├─ Document breaking changes                                        │
│    └─ Maintain backward compatibility if possible                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow

### 2.1 Phase Completion Flow

```
Start Phase
    ↓
Implement Scope (2-3 hours)
    ├─ Implemented items: Full implementation
    └─ Stubbed items: raise NotImplementedError()
    ↓
Run Verification
    ├─ Health check: curl /health returns 200
    ├─ Unit tests: pytest passes
    └─ Integration tests: pytest passes
    ↓
Freeze APIs
    ├─ Document all public APIs
    ├─ Mark as frozen in API docs
    └─ Tag version in git
    ↓
Phase Complete (usable/releasable)
    ↓
Next Phase (or done if Phase 7)
```

### 2.2 Dependency Satisfaction Flow

```
Start Phase N
    ↓
Check Dependencies
    ├─ Phase N-1 complete? ──No──→ Block, wait for N-1
    └─ Required changes complete? ──No──→ Block, wait for changes
    ↓
All Dependencies Satisfied
    ↓
Use Frozen APIs from Previous Phases
    ├─ Read API documentation
    ├─ Import frozen modules
    └─ No breaking changes allowed
    ↓
Implement Phase N
```

### 2.3 Verification Flow

```
Phase Implementation Complete
    ↓
Health Check
    ├─ GET /health → 200 OK
    ├─ Check component status
    └─ Verify all services responding
    ↓
Unit Tests
    ├─ pytest tests/unit/
    ├─ Cover all implemented code
    └─ Stubbed items may be skipped
    ↓
Integration Tests
    ├─ pytest tests/integration/
    ├─ Test component interactions
    └─ Verify phase functionality
    ↓
Coverage Report (Phase 7 only)
    ├─ pytest --cov=agentx --cov-report=html
    ├─ Verify >70% coverage
    └─ Review uncovered lines
    ↓
All Checks Pass → Phase Complete
```

---

## 3. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| **8 phases of 2-3 hours** | Incremental delivery | Big bang (1 phase), 4 phases (too large), 16 phases (too granular) | Manageable chunks, fits in half-day sprints |
| **API freezing** | Freeze after each phase | No freezing, Continuous API evolution | Enables parallel development, clear contracts |
| **Linear dependency chain** | 0→1→2→3→4→5→6→7 | Parallel starts, Circular dependencies | Simple ordering, clear progression |
| **Stubbed items with NotImplementedError** | Explicit stubs | Comment-only stubs, No stubs | Clear what's implemented, testable |
| **Verification per phase** | Health + unit + integration tests | Big bang testing, Manual verification | Continuous validation, early issue detection |
| **Semantic versioning** | Major version for breaking changes | No versioning, Date-based versioning | Clear compatibility, standard practice |
| **LLD as source of truth** | Locked LLD sections | Working specs as source | Prevents drift, single source of truth |

---

## 4. Tradeoff Analysis

### 4.1 Approach A: Big Bang Delivery (Single Phase)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐ | Single implementation phase |
| Progress Visibility | ⭐ | No working system until complete |
| Risk | Low risk accumulation, late discovery | |
| Parallel Development | ❌ | Teams blocked on each other |

**Pros**:
- Simple planning (one large milestone)
- No API compatibility concerns

**Cons**:
- No intermediate releases
- Late validation (integration issues at end)
- Blocked parallel development
- High risk (all-or-nothing)

### 4.2 Approach B: Incremental Delivery (Chosen)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐ | Requires phase planning |
| Progress Visibility | ⭐⭐⭐ | Each phase is usable/releasable |
| Risk | Low risk per phase, early discovery | |
| Parallel Development | ⭐⭐⭐ | Enabled after API freezing |

**Pros**:
- Each phase produces usable system
- Early validation (issues caught immediately)
- Parallel development (after API freezing)
- Clear progress (8 milestones)
- Lower risk (failure isolated to phase)

**Cons**:
- More complex planning (8 phases)
- API freezing requires discipline
- More documentation (frozen APIs)

### 4.3 Decision: Incremental Delivery

**Rationale**: The benefits far outweigh complexity. Big bang delivery is too risky for a system of this scope. Incremental delivery provides:
- Manageable 2-3 hour chunks
- Continuous validation
- Parallel development potential
- Clear progress indicators
- Reduced risk

---

## 5. Implementation Details

### 5.1 Phase Duration Management

| Strategy | Implementation |
|----------|----------------|
| **Time tracking** | Track start/end time for each phase |
| **Scope limits** | If phase exceeds 3 hours, split into sub-phases |
| **Stubbed items** | Defer non-critical features with NotImplementedError |
| **Velocity measurement** | Track actual vs estimated time, adjust future estimates |

### 5.2 API Freezing Process

```
Phase Complete
    ↓
Document APIs
    ├─ List all public functions/classes
    ├─ Document signatures
    └─ Add examples
    ↓
Mark as Frozen
    ├─ Add @freeze decorator or comment
    ├─ Update API documentation
    └─ Tag version in git (v1.0.0, v2.0.0, etc.)
    ↓
Notify Dependent Teams
    ├─ Publish API documentation
    ├─ Send notification of frozen APIs
    └─ Update dependency graph
```

### 5.3 Verification Framework

```python
# tests/conftest.py (shared fixtures)
@pytest.fixture
def test_settings():
    """Test settings with minimal config."""
    return Settings(model="gemma3:4b", debug=True)

@pytest.fixture
def test_client(test_settings):
    """FastAPI test client."""
    from core.main import app
    return TestClient(app)

# tests/unit/test_phase_0.py
def test_health_check(test_client):
    """Phase 0: Health check returns 200."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# tests/integration/test_phase_2.py
def test_agent_calculator(test_client):
    """Phase 2: Agent returns calculator results."""
    response = test_client.post(
        "/api/v1/agent/query",
        json={"query": "What is 123 * 456?"}
    )
    assert response.status_code == 200
    assert "56088" in response.json()["answer"]
```

### 5.4 Port Assignments

| Phase | Ports | Purpose |
|-------|-------|---------|
| **Phase 0** | 8000 | Main API server |
| **Phase 3** | 8016 | WebSocket streaming |
| **Phase 4** | 8015-8017 | Agent services |
| **Phase 5** | 8021-8022 | Memory services |
| **Phase 7** | All above | Complete system |

---

## 6. Security Considerations

| Concern | Mitigation |
|---------|------------|
| **API abuse** | Rate limiting per user (Phase 7) |
| **Input validation** | Pydantic models on all endpoints (Phase 7) |
| **PII leakage** | No logging of user data, PII redaction (Phase 7) |
| **Plugin sandboxing** | Permission enforcement, code signing (Phase 6) |
| **Memory injection** | User ID validation, content sanitization (Phase 5) |

---

## 7. Performance Considerations

| Concern | Mitigation |
|---------|------------|
| **Phase completion time** | Strict 2-3 hour limit, defer non-critical features |
| **Health check latency** | Target <1 second for all health checks |
| **Unit test execution** | Target <5 minutes for full unit test suite |
| **Integration test execution** | Target <10 minutes for full integration suite |
| **Parallel development** | API freezing enables multiple teams |
| **Code coverage** | Target 70% in Phase 7, use pytest-cov |

---

## 8. Integration Points

### 8.1 C001 Folder Structure Integration

```python
# Phase 0 uses C001 structure
agentx/
├── core/              # From C001: Configuration
│   └── config.py
├── domain/            # From C001: Business entities (Phase 1)
│   └── entities/
├── infrastructure/    # From C001: External services (Phase 1)
│   └── database/
├── application/       # From C001: Use cases (Phase 2+)
│   └── use_cases/
└── presentation/      # From C001: FastAPI routes (Phase 0)
    └── api/v1/
```

### 8.2 C002 Data Contracts Integration

```python
# Phase 2+ uses C002 Pydantic → Zod alignment
from application.dtos.agent_dtos import ExecuteAgentQueryCommand

# Backend (Pydantic v2)
class ExecuteAgentQueryCommand(BaseModel):
    session_id: UUID
    query: str = Field(..., min_length=1)
    stream: bool = Field(default=False)

# Frontend (Zod) - generated from C002 patterns
export const ExecuteAgentQueryCommandSchema = z.object({
  session_id: z.string().uuid(),
  query: z.string().min(1),
  stream: z.boolean().default(false),
});
```

### 8.3 C003 Agent Pipeline Integration

```python
# Phase 2-4 use C003 agents
from agent.agents.main_dspy_react import MainDSPyReActAgent
from agent.agents.ui_dspy import UIDSPyAgent
from agent.agents.rag_dspy import RAGDSPyAgent

# Phase 2: MainDSPyReActAgent
main_agent = MainDSPyReActAgent(tools=[...])

# Phase 3: UIDSPyAgent
ui_agent = UIDSPyAgent(...)

# Phase 4: LangGraph state machines
from agent.state_machines.backend_langgraph import BackendLangGraphState
```

### 8.4 C004 Voice Streaming Integration

```python
# Phase 7 uses C004 voice services
from infrastructure.voice.stt_service import STTService
from infrastructure.voice.tts_service import TTSService
from infrastructure.voice.vad_service import VADService

# Voice pipeline integration (Phase 7)
voice_pipeline = VoicePipeline(
    stt=STTService(...),
    tts=TTSService(...),
    vad=VADService(...)
)
```

### 8.5 C005 Memory RAG Integration

```python
# Phase 5 uses C005 memory services
from application.services.temporal_rag_service import TemporalRAGService
from application.use_cases.consolidate_memory_use_case import ConsolidateMemoryUseCase

# Memory integration (Phase 5)
rag_service = TemporalRAGService(...)
consolidation_use_case = ConsolidateMemoryUseCase(...)
```

---

## 9. Risk Mitigation

### 9.1 Phase Duration Risks

| Risk | Mitigation |
|------|------------|
| **Phase takes >3 hours** | Strict scope limits, stub non-critical items |
| **Scope creep** | Document scope boundaries, defer to later phases |
| **Underestimation** | Track velocity, adjust future estimates |

### 9.2 API Freezing Risks

| Risk | Mitigation |
|------|------------|
| **Breaking change needed** | Create new major version, maintain backward compatibility |
| **Incomplete API documentation** | Require API docs as part of phase completion |
| **API drift** | Lock LLD definitions, review changes |

### 9.3 Dependency Risks

| Risk | Mitigation |
|------|------------|
| **C001-C005 not ready** | Verify all changes complete before Phase 0 |
| **Integration issues** | Phase 7 dedicated to hardening and integration |
| **Parallel development conflicts** | Clear API contracts, frozen APIs |

---

**Next Artifact**: tasks.md
