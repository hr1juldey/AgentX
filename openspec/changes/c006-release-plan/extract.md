# Extract Artifact: c006-release-plan

**Generated**: 2026-01-28
**Change**: c006-release-plan
**Schema**: spec-factory v1

---

## 1. Pattern Catalog

### 1.1 Architectural Patterns

| Pattern | Source | Description | Apply? |
|---------|--------|-------------|--------|
| **Incremental Build** | incremental_release_plan.md | 8-phase delivery (0→1→2→3→4→5→6→7) | ✅ |
| **API Freezing** | incremental_release_plan.md | Freeze APIs after each phase | ✅ |
| **Clean Architecture** | mimicus + C001 | Layered separation (core/, domain/, application/, infrastructure/, presentation/) | ✅ |
| **Repository Pattern** | mimicus + C001 | ABC base + implementations | ✅ |
| **DTO Pattern** | mimicus + C002 | Pydantic models for API layer | ✅ |
| **Use Case Pattern** | mimicus + C001 | Single-purpose classes with execute() | ✅ |
| **Dependency Injection** | C001 | Global singletons + getter functions | ✅ |

### 1.2 Code Structure Patterns

| Pattern | Example | Apply? |
|---------|---------|--------|
| @dataclass entities | `class AgentSessionEntity:` | ✅ |
| ABC repositories | `class AgentSessionRepository(ABC):` | ✅ |
| Static mappers | `@staticmethod def to_dto()` | ✅ |
| Use case classes | `class ExecuteAgentQueryUseCase:` | ✅ |
| Phase stubbing | `raise NotImplementedError()` | ✅ |
| Pydantic v2 syntax | `str \| None`, `Literal["a", "b"]` | ✅ |
| Zod frontend types | `z.object()`, `z.enum()` | ✅ |

### 1.3 Naming Patterns (to Avoid)

| Pattern | Why Avoid | Alternative |
|-----------|-----------|-------------|
| **Skipping phases** | Breaks incremental delivery | Follow 0→1→2→3→4→5→6→7 order |
| **Changing frozen APIs** | Breaks dependent phases | Use new version for breaking changes |
| **Implementing too much** | Violates 2-3 hour target | Stick to phase scope |
| **Not stubbing properly** | Confusing what's implemented | Use NotImplementedError clearly |
| **No verification** | Can't validate phase completion | Add verification criteria for each phase |

---

## 2. Specification Drafts

### 2.1 Draft: incremental-delivery Spec

**Purpose**: Define the 8-phase incremental delivery strategy that builds AgentX from minimal server to production-hardened system.

**Scope**:
- In scope: 8-phase implementation plan, API freezing rules, verification criteria, dependency ordering
- Out of scope: Individual phase implementation (covered by C001-C005), post-release maintenance

**Locked from LLD**:

```python
# incremental_release_plan.md:36-48 (LOCKED)
Phase Overview:
- Phase 0: Server Setup (2-3 hours)
- Phase 1: Domain + Infrastructure (2-3 hours)
- Phase 2: Main DSPy Agent (2-3 hours)
- Phase 3: UI + Streaming (2-3 hours)
- Phase 4: State Machines (2-3 hours)
- Phase 5: Memory + RAG (2-3 hours)
- Phase 6: Plugins (2-3 hours)
- Phase 7: Production Hardening (2-3 hours)

Incremental Delivery Principles:
- Each phase must be usable/releasable after completion
- Take 2-3 hours to implement
- Build on previous phases
- Have frozen APIs (no breaking changes)
- Have verification criteria
```

**Requirements**:
1. **FR-ID-001**: Each phase MUST complete in 2-3 hours
2. **FR-ID-002**: Each phase MUST freeze its APIs upon completion
3. **FR-ID-003**: Each phase MUST pass verification criteria
4. **FR-ID-004**: Phases MUST be implemented in order (0→1→2→3→4→5→6→7)
5. **FR-ID-005**: Breaking changes require new major version
6. **FR-ID-006**: All stubbed items MUST use NotImplementedError

**Acceptance Criteria**:
- [ ] All 8 phases defined with scope and deliverables
- [ ] API freezing rules documented
- [ ] Verification criteria for each phase
- [ ] Dependency graph established
- [ ] Integration with C001-C005 specifications

---

### 2.2 Draft: api-freezing Spec

**Purpose**: Define the API freezing strategy that enables parallel development across phases while maintaining compatibility.

**Scope**:
- In scope: API freeze rules, breaking change policy, versioning strategy
- Out of scope: Specific API definitions (covered by C001-C005)

**Locked from LLD**:

```python
# incremental_release_plan.md:31-34 (LOCKED)
API Freezing Rules:
- Once a phase is complete, its APIs are frozen
- Subsequent phases must use existing APIs
- Breaking changes require new major version
```

**Requirements**:
1. **FR-AF-001**: Frozen APIs MUST NOT change signatures
2. **FR-AF-002**: Frozen APIs MUST NOT break backward compatibility
3. **FR-AF-003**: Breaking changes MUST increment major version
4. **FR-AF-004**: API freeze MUST be documented in phase completion

**Acceptance Criteria**:
- [ ] API freeze rules enforced across all phases
- [ ] Breaking change process defined
- [ ] Versioning strategy established
- [ ] Documentation updated for each frozen API

---

### 2.3 Draft: verification-criteria Spec

**Purpose**: Define verification criteria for each phase to ensure completion and quality.

**Scope**:
- In scope: Verification tests for all 8 phases, health checks, integration tests
- Out of scope: Continuous monitoring (post-release concern)

**Locked from LLD**:

Each phase has verification criteria (from incremental_release_plan.md):
- Phase 0: `curl http://localhost:8000/health` returns 200
- Phase 1: Entity creation, repository CRUD tests pass
- Phase 2: Agent returns correct calculator results
- Phase 3: Descriptor creation, WebSocket message tests pass
- Phase 4: State machine transitions IDLE → COMPLETED
- Phase 5: Memory storage, retrieval tests pass
- Phase 6: Plugin lifecycle, permission enforcement tests pass
- Phase 7: All tests pass, coverage >70%, load test succeeds

**Requirements**:
1. **FR-VC-001**: Each phase MUST have verification criteria
2. **FR-VC-002**: Health check MUST return 200 for all components
3. **FR-VC-003**: Unit tests MUST pass for all implemented code
4. **FR-VC-004**: Integration tests MUST pass for phase functionality
5. **FR-VC-005**: Phase 7 MUST achieve 70% code coverage

**Acceptance Criteria**:
- [ ] All 8 phases have verification criteria
- [ ] Health check endpoint exists
- [ ] Unit test framework configured
- [ ] Integration test framework configured
- [ ] Coverage reporting enabled

---

## 3. API Contracts

### 3.1 REST Endpoints

| Phase | Endpoints | Purpose |
|-------|-----------|---------|
| **Phase 0** | `GET /health`, `GET /api/v1/config` | Server health, config |
| **Phase 2** | `POST /api/v1/agent/query` | Agent query execution |
| **Phase 3** | `WS /ws/ui` | UI descriptor streaming |
| **Phase 5** | `POST /api/v1/memory/store`, `POST /api/v1/memory/search` | Memory operations |
| **Phase 7** | `GET /health`, `GET /metrics` | Component health, metrics |

### 3.2 Port Assignments

| Phase | Ports | Purpose |
|-------|-------|---------|
| **Phase 0** | 8000 | Main API server |
| **Phase 3** | 8016 | WebSocket streaming |
| **Phase 4** | 8015-8017 | Agent services |
| **Phase 5** | 8021-8022 | Memory services |
| **Phase 7** | All above | Complete system |

### 3.3 Health Check Endpoints

| Component | Endpoint | Response |
|-----------|----------|--------|
| **Server** | `GET /health` | `{"status": "healthy", "components": {...}}` |
| **Agent** | `GET /api/v1/agent/health` | Agent status, DSPy connection |
| **Memory** | `GET /api/v1/memory/health` | Qdrant, Mem0AI status |
| **Voice** | `GET /api/v1/voice/health` | VAD, STT, TTS status |

---

## 4. Data Model Mappings

### 4.1 Shared DTOs (Across Phases)

| DTO | Phase | Zod Type |
|-----|-------|----------|
| `Settings` | Phase 0 | `SettingsSchema` |
| `ExecuteAgentQueryCommand` | Phase 2 | `ExecuteAgentQueryCommandSchema` |
| `CardDescriptor` | Phase 3 | `CardDescriptorSchema` |
| `StoreMemoryCommand` | Phase 5 | `StoreMemoryCommandSchema` |

### 4.2 Pydantic → Zod Alignment

**Phase 2 Example**:
```python
# Backend (Pydantic v2)
class ExecuteAgentQueryCommand(BaseModel):
    session_id: UUID
    query: str = Field(..., min_length=1)
    stream: bool = Field(default=False)
```

```typescript
// Frontend (Zod)
export const ExecuteAgentQueryCommandSchema = z.object({
  session_id: z.string().uuid(),
  query: z.string().min(1),
  stream: z.boolean().default(false),
});
```

---

## 5. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| **C001-folder-structure** | Structural | Provides Clean Architecture layers for all phases |
| **C002-data-contracts** | Contract | Defines Pydantic v2 → Zod alignment pattern |
| **C003-agent-pipeline** | Functional | Phase 2-4 depend on DSPy agents, LangGraph |
| **C004-voice-streaming** | Functional | Phase 7 depends on voice services |
| **C005-memory-rag** | Functional | Phase 5 depends on memory services |

### 5.1 Phase Dependency Graph

```
Phase 0 (Server) ────────┐
                         │
Phase 1 (Domain) ───────┤
                         │
Phase 2 (Agent) ────────┤
                         │
Phase 3 (UI) ──────────┤
                         │
Phase 4 (State) ───────┤
                         │
Phase 5 (Memory) ─────┤
                         │
Phase 6 (Plugins) ────┤
                         │
Phase 7 (Hardening) ──┴─────────────┘ (depends on ALL)
```

### 5.2 Change → Phase Mapping

| Change | Phases Enabled |
|--------|-----------------|
| **C001-folder-structure** | All phases (foundation) |
| **C002-data-contracts** | Phases 2+ (DTOs required) |
| **C003-agent-pipeline** | Phases 2-4 (DSPy + LangGraph) |
| **C004-voice-streaming** | Phase 7 (voice integration) |
| **C005-memory-rag** | Phase 5 (memory services) |

---

**Next Artifact**: validate.md
