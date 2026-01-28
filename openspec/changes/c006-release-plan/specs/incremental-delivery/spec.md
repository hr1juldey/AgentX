# Spec: incremental-delivery

**File**: `specs/incremental-delivery/spec.md`

## 1.1 Purpose

Define the 11-phase incremental delivery strategy that builds AgentX from minimal server to production-hardened system with frontend. Each phase is independently usable/releasable, takes 2-3 hours to implement, builds on previous phases, and has frozen APIs.

## 1.2 Scope

**In Scope**:
- 11-phase implementation plan (Phase 0-10)
- API freezing rules (no breaking changes after phase completion)
- Verification criteria (health checks, tests)
- Dependency ordering (linear 0→1→2→3→4→5→6→7→8→9→10)
- Frontend phases (C007-C009) integrated after backend completion

**Out of Scope**:
- Individual phase implementation (covered by C001-C009)
- Post-release maintenance (monitoring, updates)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ID-001 | Each phase MUST complete in 2-3 hours | Must |
| FR-ID-002 | Each phase MUST freeze its APIs upon completion | Must |
| FR-ID-003 | Each phase MUST pass verification criteria | Must |
| FR-ID-004 | Backend phases (0-6) MUST be implemented before frontend phases (7-9) | Must |
| FR-ID-005 | Breaking changes require new major version | Must |
| FR-ID-006 | All stubbed items MUST use NotImplementedError | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-ID-001 | Each phase MUST be usable/releasable after completion | Must |
| NFR-ID-002 | API freeze MUST be documented in phase completion | Must |
| NFR-ID-003 | Phase dependencies MUST be explicit | Should |

## 1.4 Phase Definitions (Updated with C007-C009)

**Backend Phases** (C001-C006):

| Phase | Duration | Focus | Deliverables | APIs Frozen | Change |
|-------|----------|-------|--------------|-------------|--------|
| **Phase 0** | 2-3 hours | Server Setup | FastAPI, Config, DI | Settings structure | C001 |
| **Phase 1** | 2-3 hours | Domain + Infrastructure | Entities, Repositories, Adapters | Entity structures | C001 |
| **Phase 2** | 2-3 hours | Data Contracts | Pydantic v2, Zod schemas, LangGraph UI | Data model schemas | C002 |
| **Phase 3** | 2-3 hours | Main Agent | DSPy ReAct, Tools, LangGraph | Agent signature | C003 |
| **Phase 4** | 2-3 hours | Voice Streaming | STT/TTS, VAD, WebSocket | Voice API contracts | C004 |
| **Phase 5** | 2-3 hours | Memory + RAG | Mem0AI, RAG Agent, Consolidation | RAG interface | C005 |
| **Phase 6** | 2-3 hours | Plugins | Plugin interface, Permissions | Plugin protocol | C006 |

**Frontend Phases** (C007-C009):

| Phase | Duration | Focus | Deliverables | APIs Frozen | Change |
|-------|----------|-------|--------------|-------------|--------|
| **Phase 7** | 2-3 hours | Frontend Architecture | LangGraph SDK, LoadExternalComponent, UI components | Frontend integration | C007 |
| **Phase 8** | 2-3 hours | Organic UI | Metaballs, Voice Nucleus, Design Tokens | UI visual layer | C008 |
| **Phase 9** | 2-3 hours | UI Polish | Raycast minimalism, Google Assistant clarity | Aesthetic fixes | C009 |
| **Phase 10** | 2-3 hours | Hardening | Tests, Error handling, Monitoring | Complete system | C006 |

## 1.5 Phase Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AgentX v0.1 Phase Dependencies                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Backend (C001-C006):                    Frontend (C007-C009):          │
│                                                                         │
│  Phase 0 (Server Setup)                                                 │
│    ↓                                                                    │
│  Phase 1 (Domain + Infrastructure)                                       │
│    ↓                                                                    │
│  Phase 2 (Data Contracts) ─────────────────────────────────┐            │
│    ↓                                                       │            │
│  Phase 3 (Agent Pipeline) ──────────────────────────────┐   │            │
│    ↓                                                      │   │            │
│  Phase 4 (Voice Streaming)                               │   │            │
│    ↓                                                      │   │            │
│  Phase 5 (Memory + RAG)                                 │   │            │
│    ↓                                                      │   │            │
│  Phase 6 (Plugins)                                       │   │            │
│    ↓                                                      │   │            │
│  [Backend Complete] ──────────────────────────────────────┘   │            │
│           ↓                                                     │            │
│           │                                                     │            │
│           └─────────────────────────────────────────────────────┼────────────┘
│                                                                 │
│                                                                 ↓
│  Phase 7 (Frontend Architecture) ←──┐                            │
│    ↓                                │                            │
│  Phase 8 (Organic UI)               │                            │
│    ↓                                │                            │
│  Phase 9 (UI Polish)                │                            │
│    ↓                                │                            │
│  Phase 10 (Hardening) ◀─────────────┘                            │
│    ↓                                                             │
│  [Production Release]                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

## 1.6 API Contract

### Health Check Endpoints

| Phase | Endpoint | Response | Status |
|-------|----------|--------|--------|
| **Phase 0** | `GET /health` | `{"status": "healthy"}` | Backend |
| **Phase 3** | `GET /api/v1/agent/health` | Agent status, LangGraph connection | Backend |
| **Phase 4** | `GET /api/v1/voice/health` | VAD, STT, TTS status | Backend |
| **Phase 5** | `GET /api/v1/memory/health` | Qdrant, Mem0AI status | Backend |
| **Phase 7** | `GET /api/v1/health` | LangGraph server status | Frontend |
| **Phase 10** | `GET /health` | Component health, metrics | Complete |

### Port Assignments

| Phase | Service | Port | Protocol |
|-------|---------|------|----------|
| **Phase 0-2** | FastAPI Backend | 2024 | HTTP |
| **Phase 3** | LangGraph Server | 2024 | HTTP |
| **Phase 4** | Voice API | 8018 | HTTP |
| **Phase 4** | Voice WebSocket | 8019 | WS |
| **Phase 4** | Voice Health | 8020 | HTTP |
| **Phase 7** | Frontend (Next.js) | 3000 | HTTP |
| **Phase 10** | Production (All) | As above | HTTP/WS |

## 1.7 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-ID-001 | Phase duration MUST be 2-3 hours | Project planning, scope limits |
| BR-ID-002 | APIs frozen after phase completion | Documentation, version control |
| BR-ID-003 | Stubbed items raise NotImplementedError | Code review |
| BR-ID-004 | Phases implemented in order | Dependency check before starting |
| BR-ID-005 | Breaking changes increment major version | Semantic versioning |
| BR-ID-006 | Frontend phases (7-9) depend on backend completion | Dependency check |

## 1.8 Acceptance Criteria

- [ ] All 11 phases defined with scope and deliverables
- [ ] API freezing rules documented
- [ ] Verification criteria for each phase
- [ ] Dependency graph established (0→1→2→3→4→5→6→7→8→9→10)
- [ ] Integration with C001-C009 specifications
- [ ] Each phase has health check endpoint
- [ ] Each phase has 2-3 hour duration target
- [ ] Frontend phases (7-9) clearly depend on backend completion
- [ ] LangGraph server-driven UI architecture documented in Phase 7
- [ ] Organic UI visual layer documented in Phase 8
- [ ] UI polish requirements documented in Phase 9

## 1.9 Phase Completion Criteria

### Backend Phases (0-6)

| Phase | Verification Criteria | Health Check |
|-------|----------------------|--------------|
| **Phase 0** | FastAPI server running, config loaded | `GET /health` |
| **Phase 1** | Entities, repositories, adapters implemented | `GET /health` |
| **Phase 2** | Pydantic ↔ Zod schemas match, LangGraph UI ready | `GET /health` |
| **Phase 3** | LangGraph graph executes, nodes connected | `GET /api/v1/agent/health` |
| **Phase 4** | Voice pipeline works end-to-end | `GET /api/v1/voice/health` |
| **Phase 5** | Memory consolidation, RAG functional | `GET /api/v1/memory/health` |
| **Phase 6** | Plugin system loads external plugins | `GET /health` |

### Frontend Phases (7-9)

| Phase | Verification Criteria | Health Check |
|-------|----------------------|--------------|
| **Phase 7** | `useStream()` connects, `LoadExternalComponent` renders | `GET /api/v1/health` |
| **Phase 8** | Metaballs animate, Voice Nucleus displays | Visual inspection |
| **Phase 9** | UI matches Raycast/Google Assistant aesthetic | Visual inspection |

### Hardening Phase (10)

| Verification Criteria |
|----------------------|
| All tests passing (pytest, Jest) |
| Code quality checks passing (ruff, tsc) |
| Error handling complete |
| Monitoring/logging configured |

---

**Related Specs**:
- `specs/api-freezing/spec.md` - API freezing strategy
- C001-C009 - Individual phase specifications
