# Specs Artifact: c006-release-plan

**Generated**: 2026-01-29 (Updated with C007-C009 frontend phases)
**Change**: c006-release-plan
**Schema**: spec-factory v1

---

## 1. Spec: incremental-delivery

**File**: `specs/incremental-delivery/spec.md`

**Purpose**: Define the 11-phase incremental delivery strategy that builds AgentX from minimal server to production-hardened system with frontend.

**Key Requirements**:
- 11 phases (0-10), 2-3 hours each
- Backend phases (0-6): Server → Domain → Data → Agent → Voice → Memory → Plugins
- Frontend phases (7-9): Architecture → Organic UI → Polish
- Hardening phase (10): Tests, errors, monitoring
- APIs frozen after each phase completion

**Phase Sequence**:
```
0 (Server) → 1 (Domain) → 2 (Data) → 3 (Agent) → 4 (Voice) → 5 (Memory) → 6 (Plugins)
 → 7 (Frontend Arch) → 8 (Organic UI) → 9 (UI Polish) → 10 (Hardening)
```

**Acceptance Criteria**:
- [ ] All 11 phases defined with scope
- [ ] API freezing rules documented
- [ ] Dependency graph established
- [ ] Frontend phases (7-9) depend on backend completion
- [ ] LangGraph server-driven UI in Phase 7
- [ ] Organic UI visual layer in Phase 8
- [ ] UI polish requirements in Phase 9

---

## 2. Spec: api-freezing

**File**: `specs/api-freezing/spec.md`

**Purpose**: Define the API freezing strategy that enables parallel development while maintaining compatibility.

**Key Requirements**:
- APIs frozen when phase completes
- No breaking changes without major version increment
- Widget names must match backend `push_ui_message()` calls
- Design tokens frozen once defined

**Frozen Categories**:
- Entity fields, repository methods, Pydantic/Zod schemas
- Agent signatures, voice API, RAG interface
- Widget names, design tokens

**Acceptance Criteria**:
- [ ] API freezing rules documented
- [ ] Breaking change policy defined
- [ ] Versioning strategy established (semver)
- [ ] Phase completion checklist created
- [ ] Widget name freezing rules (from C007)

---

## 3. Phase Overview

### Backend Phases (C001-C006)

| Phase | Focus | Duration | Deliverables | APIs Frozen |
|-------|-------|----------|--------------|-------------|
| **0** | Server Setup | 2-3h | FastAPI, Config, DI | Settings |
| **1** | Domain + Infra | 2-3h | Entities, Repos | Entities |
| **2** | Data Contracts | 2-3h | Pydantic, Zod, LangGraph UI | Schemas |
| **3** | Agent Pipeline | 2-3h | DSPy ReAct, LangGraph | Agent sig |
| **4** | Voice Streaming | 2-3h | STT/TTS, VAD, WS | Voice API |
| **5** | Memory + RAG | 2-3h | Mem0AI, RAG, Consolidation | RAG iface |
| **6** | Plugins | 2-3h | Plugin interface, Permissions | Plugin proto |

### Frontend Phases (C007-C009)

| Phase | Focus | Duration | Deliverables | APIs Frozen |
|-------|-------|----------|--------------|-------------|
| **7** | Frontend Arch | 2-3h | LangGraph SDK, LoadExternalComponent | Frontend int |
| **8** | Organic UI | 2-3h | Metaballs, Voice Nucleus, Tokens | Visual layer |
| **9** | UI Polish | 2-3h | Raycast minimalism, GA clarity | Aesthetics |

### Hardening Phase

| Phase | Focus | Duration | Deliverables | APIs Frozen |
|-------|-------|----------|--------------|-------------|
| **10** | Hardening | 2-3h | Tests, Errors, Monitoring | Complete |

---

## 4. Dependency Graph

```
Backend (C001-C006) → Frontend (C007-C009) → Hardening (C006)
    0→1→2→3→4→5→6         7→8→9                10
```

**Critical Path**: Backend must complete before frontend starts (Phase 6 → Phase 7)

---

## 5. Port Assignments

| Service | Port | Phase |
|---------|------|-------|
| LangGraph Server | 2024 | 3+ |
| Voice API | 8018 | 4+ |
| Voice WebSocket | 8019 | 4+ |
| Voice Health | 8020 | 4+ |
| Frontend (Next.js) | 3000 | 7+ |

---

## 6. Version Milestones

| Version | Phases | Description |
|---------|--------|-------------|
| `0.1.0` | 0-2 | Backend MVP (server, domain, data) |
| `0.2.0` | 3-5 | Agent + Voice + Memory |
| `0.3.0` | 6 | Plugins |
| `0.4.0` | 7 | Frontend Architecture |
| `0.5.0` | 8 | Organic UI |
| `0.6.0` | 9 | UI Polish |
| `1.0.0` | 10 | Production Release |

---

## 7. Frontend Integration (from C007)

### LangGraph Server-Driven UI

Phase 7 establishes the frontend architecture pattern:
- Backend emits UI via `push_ui_message(component_name, props)`
- Frontend renders via `LoadExternalComponent`
- Components colocated in `agent/ui.tsx`
- State tracking via `ui_message_reducer`

### Widget Name Freezing

Once widget names are defined in Phase 7, they are frozen:
```python
# Backend (frozen)
push_ui_message("card", {...})
```

```typescript
// Frontend (frozen)
export default {
  card: CardComponent,  // Name: "card" frozen
};
```

---

**Next Artifact**: design.md
