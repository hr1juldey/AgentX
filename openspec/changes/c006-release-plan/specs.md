# Specs Artifact: c006-release-plan

**Generated**: 2026-01-28
**Change**: c006-release-plan
**Schema**: spec-factory v1

---

## Spec Structure

This artifact generates domain-specific specification files in `specs/{domain}/spec.md`.

---

## 1. Spec: incremental-delivery

**File**: `specs/incremental-delivery/spec.md`

### 1.1 Purpose

Define the 8-phase incremental delivery strategy that builds AgentX from minimal server to production-hardened system. Each phase is independently usable/releasable, takes 2-3 hours to implement, builds on previous phases, and has frozen APIs.

### 1.2 Scope

**In Scope**:
- 8-phase implementation plan (Phase 0-7)
- API freezing rules (no breaking changes after phase completion)
- Verification criteria (health checks, tests)
- Dependency ordering (linear 0→1→2→3→4→5→6→7)

**Out of Scope**:
- Individual phase implementation (covered by C001-C005)
- Post-release maintenance (monitoring, updates)

### 1.3 Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ID-001 | Each phase MUST complete in 2-3 hours | Must |
| FR-ID-002 | Each phase MUST freeze its APIs upon completion | Must |
| FR-ID-003 | Each phase MUST pass verification criteria | Must |
| FR-ID-004 | Phases MUST be implemented in order (0→1→2→3→4→5→6→7) | Must |
| FR-ID-005 | Breaking changes require new major version | Must |
| FR-ID-006 | All stubbed items MUST use NotImplementedError | Must |

#### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-ID-001 | Each phase MUST be usable/releasable after completion | Must |
| NFR-ID-002 | API freeze MUST be documented in phase completion | Must |
| NFR-ID-003 | Phase dependencies MUST be explicit | Should |

### 1.4 Phase Definitions

**Locked from LLD** (incremental_release_plan.md:36-48):

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

### 1.5 API Contract

#### Health Check Endpoints

| Phase | Endpoint | Response |
|-------|----------|--------|
| **Phase 0** | `GET /health` | `{"status": "healthy"}` |
| **Phase 2** | `GET /api/v1/agent/health` | Agent status, DSPy connection |
| **Phase 3** | `GET /ws/ui/health` | WebSocket status |
| **Phase 5** | `GET /api/v1/memory/health` | Qdrant, Mem0AI status |
| **Phase 7** | `GET /health` | Component health, metrics |

### 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-ID-001 | Phase duration MUST be 2-3 hours | Project planning, scope limits |
| BR-ID-002 | APIs frozen after phase completion | Documentation, version control |
| BR-ID-003 | Stubbed items raise NotImplementedError | Code review |
| BR-ID-004 | Phases implemented in order | Dependency check before starting |
| BR-ID-005 | Breaking changes increment major version | Semantic versioning |

### 1.7 Acceptance Criteria

- [ ] All 8 phases defined with scope and deliverables
- [ ] API freezing rules documented
- [ ] Verification criteria for each phase
- [ ] Dependency graph established (0→1→2→3→4→5→6→7)
- [ ] Integration with C001-C005 specifications
- [ ] Each phase has health check endpoint
- [ ] Each phase has 2-3 hour duration target

---

## 2. Spec: api-freezing

**File**: `specs/api-freezing/spec.md`

### 2.1 Purpose

Define the API freezing strategy that enables parallel development across phases while maintaining compatibility. Once a phase is complete, its APIs are frozen - no breaking changes allowed.

### 2.2 Scope

**In Scope**:
- API freeze rules (when to freeze, what to freeze)
- Breaking change policy (how to handle required changes)
- Versioning strategy (semantic versioning)
- Documentation requirements (API docs after freeze)

**Out of Scope**:
- Specific API definitions (covered by C001-C005)
- API documentation format (Swagger/OpenAPI)

### 2.3 Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-AF-001 | Frozen APIs MUST NOT change signatures | Must |
| FR-AF-002 | Frozen APIs MUST NOT break backward compatibility | Must |
| FR-AF-003 | Breaking changes MUST increment major version | Must |
| FR-AF-004 | API freeze MUST be documented in phase completion | Must |

#### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-AF-001 | API documentation MUST be updated after freeze | Should |
| NFR-AF-002 | Breaking changes MUST be communicated | Should |

### 2.4 API Freezing Rules

**Locked from LLD** (incremental_release_plan.md:31-34):

```python
# API Freezing Rules:
# - Once a phase is complete, its APIs are frozen
# - Subsequent phases must use existing APIs
# - Breaking changes require new major version
```

### 2.5 Breaking Change Policy

| Change Type | Action | Example |
|------------|--------|---------|
| **Signature change** | New major version | `execute(query: str)` → `execute(query: str, context: dict)` |
| **Return type change** | New major version | Returns `str` → Returns `dict` |
| **Required field added** | New major version | Optional `timeout` → Required `timeout` |
| **Optional field added** | Same version (backward compatible) | Add `metadata: Optional[dict]` |
| **Bug fix** | Same version (patch) | Fix calculation error |
| **Performance improvement** | Same version (minor) | Faster algorithm, same API |

### 2.6 Versioning Strategy

**Semantic Versioning** (SemVer):
- **MAJOR**: Breaking changes (frozen APIs modified)
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

**Example**:
```
Phase 0 completes: v1.0.0
Phase 1 completes: v2.0.0 (breaking: entities changed)
Phase 2 completes: v3.0.0 (breaking: agent signature changed)
Phase 7 completes: v8.0.0 (complete system)
```

### 2.7 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-AF-001 | Frozen APIs cannot change | Code review, phase completion checklist |
| BR-AF-002 | Breaking changes need new major version | Release process |
| BR-AF-003 | Subsequent phases use existing frozen APIs | Integration tests |
| BR-AF-004 | API docs updated after freeze | Documentation check |

### 2.8 Acceptance Criteria

- [ ] API freeze rules enforced across all phases
- [ ] Breaking change process defined
- [ ] Versioning strategy established (SemVer)
- [ ] Documentation updated for each frozen API
- [ ] Integration tests verify frozen API compatibility

---

## 3. Spec: verification-criteria

**File**: `specs/verification-criteria/spec.md`

### 3.1 Purpose

Define verification criteria for each phase to ensure completion and quality. Each phase must pass health checks, unit tests, and integration tests before being considered complete.

### 3.2 Scope

**In Scope**:
- Verification tests for all 8 phases
- Health check endpoints
- Unit test framework configuration
- Integration test scenarios
- Coverage targets

**Out of Scope**:
- Continuous monitoring (post-release concern)
- Performance testing (covered by specific phase criteria)
- Security testing (covered by Phase 7)

### 3.3 Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VC-001 | Each phase MUST have verification criteria | Must |
| FR-VC-002 | Health check MUST return 200 for all components | Must |
| FR-VC-003 | Unit tests MUST pass for all implemented code | Must |
| FR-VC-004 | Integration tests MUST pass for phase functionality | Must |
| FR-VC-005 | Phase 7 MUST achieve 70% code coverage | Must |

#### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-VC-001 | Health check MUST complete within 1 second | Should |
| NFR-VC-002 | Unit tests MUST complete within 5 minutes | Should |
| NFR-VC-003 | Integration tests MUST complete within 10 minutes | Should |

### 3.4 Phase Verification Criteria

**Locked from LLD** (incremental_release_plan.md):

| Phase | Health Check | Unit Tests | Integration Tests |
|-------|--------------|------------|-------------------|
| **Phase 0** | `curl /health` returns 200 | Config, DI tests | Server starts without errors |
| **Phase 1** | `GET /health` returns components | Entity CRUD tests | Repository operations |
| **Phase 2** | `GET /api/v1/agent/health` | Agent tool tests | Agent returns calculator results |
| **Phase 3** | `GET /ws/ui/health` | Descriptor creation tests | WebSocket message flow |
| **Phase 4** | `GET /api/v1/state/health` | State transition tests | IDLE → COMPLETED flow |
| **Phase 5** | `GET /api/v1/memory/health` | Memory CRUD tests | Memory storage/retrieval |
| **Phase 6** | `GET /api/v1/plugins/health` | Plugin lifecycle tests | Plugin load/unload |
| **Phase 7** | `GET /health` shows all components | All tests pass | E2E flows, coverage >70% |

### 3.5 Health Check Response Format

```python
# Standard health check response
{
    "status": "healthy",  # or "degraded", "unhealthy"
    "version": "1.0.0",
    "components": {
        "server": {"status": "healthy"},
        "agent": {"status": "healthy", "model": "gemma3:4b"},
        "memory": {"status": "healthy", "qdrant": "connected"},
        "voice": {"status": "healthy", "stt": "ready", "tts": "ready"}
    }
}
```

### 3.6 Test Framework Requirements

| Component | Framework | Purpose |
|-----------|-----------|---------|
| **Unit Tests** | pytest | Test individual functions/classes |
| **Integration Tests** | pytest + fixtures | Test component interactions |
| **Coverage** | pytest-cov | Measure code coverage |
| **Health Checks** | curl/httpx | Verify service availability |

### 3.7 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-VC-001 | Health check required for each phase | Phase completion checklist |
| BR-VC-002 | Unit tests required for implemented code | Code review |
| BR-VC-003 | Integration tests required for phase functionality | CI/CD pipeline |
| BR-VC-004 | 70% coverage required for Phase 7 | Coverage report |
| BR-VC-005 | Stubbed items raise NotImplementedError | Code review |

### 3.8 Acceptance Criteria

- [ ] All 8 phases have verification criteria
- [ ] Health check endpoint exists for each phase
- [ ] Unit test framework configured (pytest)
- [ ] Integration test framework configured (pytest + fixtures)
- [ ] Coverage reporting enabled (pytest-cov)
- [ ] Phase 7 requires 70% code coverage
- [ ] All verification criteria documented

---

## 4. Cross-Domain Contracts

### 4.1 Shared Types

**PhaseStatus** (used by incremental-delivery):
```python
class PhaseStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
```

**APIFreezeStatus** (used by api-freezing):
```python
class APIFreezeStatus(str, Enum):
    UNFROZEN = "unfrozen"
    FROZEN = "frozen"
    DEPRECATED = "deprecated"
```

**VerificationResult** (used by verification-criteria):
```python
class VerificationResult(BaseModel):
    phase: int
    health_check: bool
    unit_tests: bool
    integration_tests: bool
    coverage_percent: Optional[float] = None
    status: Literal["passed", "failed", "partial"]
```

### 4.2 Integration Points

| Domain A | Domain B | Interface |
|----------|----------|-----------|
| **incremental-delivery** | **api-freezing** | Phase completion triggers API freeze |
| **incremental-delivery** | **verification-criteria** | Phase completion requires verification pass |
| **api-freezing** | **verification-criteria** | Frozen APIs verified by integration tests |
| **incremental-delivery** | **C001-C005** | Each phase enabled by specific changes |

### 4.3 Data Flow

```
Phase Implementation
    ↓
Code Complete (implemented + stubbed items)
    ↓
Unit Tests (pytest)
    ↓
Integration Tests (component interactions)
    ↓
Health Check (curl /health)
    ↓
API Freeze (document frozen APIs)
    ↓
Phase Complete (usable/releasable)
```

---

## 5. Pydantic → Zod Type Mappings

### 5.1 Shared DTOs

**Backend (Pydantic v2)**:
```python
class PhaseCompletion(BaseModel):
    phase: int
    status: PhaseStatus
    frozen_apis: list[str]
    verification: VerificationResult
    completed_at: datetime
```

**Frontend (Zod)**:
```typescript
export const PhaseCompletionSchema = z.object({
  phase: z.number().int().min(0).max(7),
  status: PhaseStatusSchema,
  frozen_apis: z.array(z.string()),
  verification: VerificationResultSchema,
  completed_at: z.datetime(),
});
```

---

**Next Artifact**: design.md
