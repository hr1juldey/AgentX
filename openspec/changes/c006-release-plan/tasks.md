# Tasks Artifact: c006-release-plan

**Generated**: 2026-01-28
**Change**: c006-release-plan
**Schema**: spec-factory v1

---

## 1. Implementation Checklist

### 1.1 Phase 0: Server Setup (2-3 hours)

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Create FastAPI server | `main.py` with app factory | ⬜ | CORS, logging middleware |
| Create Pydantic Settings | `core/config.py` | ⬜ | .env support, Ollama URL |
| Create DI container | `core/dependencies.py` | ⬜ | Singleton getters |
| Create health endpoint | `GET /health` | ⬜ | Returns `{"status": "healthy"}` |
| Create config endpoint | `GET /api/v1/config` | ⬜ | Returns settings (no secrets) |

**Frozen APIs**: `Settings`, `get_settings()`, app factory

**Verification**: `curl http://localhost:8000/health` returns 200

### 1.2 Phase 1: Domain + Infrastructure (2-3 hours)

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Create AgentSessionEntity | `domain/entities/agent_session.py` | ⬜ | @dataclass, LOCKED from LLD |
| Create UIComponentEntity | `domain/entities/ui_component.py` | ⬜ | @dataclass, LOCKED from LLD |
| Create MemoryConsolidationEntity | `domain/entities/memory_consolidation.py` | ⬜ | @dataclass, LOCKED from LLD |
| Create all enums | `domain/entities/enums.py` | ⬜ | SessionState, UIComponentType, etc. (LOCKED) |
| Create AgentSessionRepository | `domain/repositories/agent_session.py` | ⬜ | ABC with methods (LOCKED) |
| Create UIComponentRepository | `domain/repositories/ui_component.py` | ⬜ | ABC with methods (LOCKED) |
| Create MemoryRepository | `domain/repositories/memory.py` | ⬜ | ABC with methods (LOCKED) |
| Create Qdrant adapter | `infrastructure/database/qdrant_adapter.py` | ⬜ | Vector operations |
| Create Redis adapter | `infrastructure/database/redis_adapter.py` | ⬜ | Session storage |
| Create SQLite adapter | `infrastructure/database/sqlite_adapter.py` | ⬜ | Session storage fallback |
| Create in-memory UI repo | `infrastructure/database/in_memory_ui.py` | ⬜ | UI component storage |

**Frozen APIs**: All entity classes, all repository interfaces, all enums

**Verification**: Entity creation, repository CRUD tests pass

### 1.3 Phase 2: Main DSPy Agent (2-3 hours)

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Create MainDSPyReActAgent | `agent/agents/main_dspy_react.py` | ⬜ | Multi-signature pattern |
| Create basic tools | `agent/tools/` | ⬜ | calculator, searxng_search, weather |
| Create ToolSelectionSignature | `agent/signatures/tool_selection.py` | ⬜ | DSPy signature |
| Create ConfidenceScoringSignature | `agent/signatures/confidence.py` | ⬜ | DSPy signature |
| Create ExecuteAgentQueryUseCase | `application/use_cases/execute_agent_query.py` | ⬜ | Without streaming (stub) |
| Create agent routes | `presentation/api/v1/agent_routes.py` | ⬜ | POST /api/v1/agent/query |

**Frozen APIs**: Agent signature, tool interface

**Verification**: Agent returns correct calculator results

### 1.4 Phase 3: UI + Streaming (2-3 hours)

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Create 7 UI descriptors | `application/dtos/ui_descriptors.py` | ⬜ | Card, Button, Input, etc. (Pydantic) |
| Create UIDSPyAgent | `agent/agents/ui_dspy.py` | ⬜ | 6 signatures |
| Create UIService | `application/services/ui_service.py` | ⬜ | Descriptor creation |
| Create WebSocket manager | `infrastructure/websocket/manager.py` | ⬜ | Streaming support |
| Create WS message types | `application/dtos/ws_messages.py` | ⬜ | All message types |
| Create UI routes | `presentation/api/v1/ui_routes.py` | ⬜ | WS /ws/ui endpoint |

**Frozen APIs**: Descriptor schemas, WebSocket message types

**Verification**: Descriptor creation, WebSocket message tests pass

### 1.5 Phase 4: State Machines (2-3 hours)

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Create BackendLangGraphState | `agent/state_machines/backend_state.py` | ⬜ | TypedDict (LOCKED) |
| Create FrontendLangGraphState | `agent/state_machines/frontend_state.py` | ⬜ | TypedDict (LOCKED) |
| Create backend nodes | `agent/state_machines/backend_nodes.py` | ⬜ | start, execute_step, complete, error |
| Create frontend nodes | `agent/state_machines/frontend_nodes.py` | ⬜ | create, update, dismiss, form_submit |
| Create AgentOrchestrator | `application/services/orchestrator.py` | ⬜ | Coordination |
| Create state routes | `presentation/api/v1/state_routes.py` | ⬜ | State management endpoints |

**Frozen APIs**: State schemas

**Verification**: State machine transitions IDLE → COMPLETED

### 1.6 Phase 5: Memory + RAG (2-3 hours)

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Create RAGDSPyAgent | `agent/agents/rag_dspy.py` | ⬜ | Retrieval + injection signatures |
| Create QdrantVectorStoreAdapter | `infrastructure/database/qdrant_vector.py` | ⬜ | Tier 2 + Tier 3 |
| Create Mem0MemoryAdapter | `infrastructure/external/mem0_memory.py` | ⬜ | Consolidation |
| Create TemporalRAGService | `application/services/temporal_rag.py` | ⬜ | Time-aware search |
| Create ConsolidateMemoryUseCase | `application/use_cases/consolidate_memory.py` | ⬜ | Tier 2 → Tier 3 |
| Create memory routes | `presentation/api/v1/memory_routes.py` | ⬜ | POST /api/v1/memory/store, search |

**Frozen APIs**: RAG interface

**Verification**: Memory storage, retrieval tests pass

### 1.7 Phase 6: Plugins (2-3 hours)

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Create AgentXPlugin | `domain/plugins/agentx_plugin.py` | ⬜ | Abstract base class |
| Create PluginPermissions | `domain/entities/plugin_permissions.py` | ⬜ | Permission types |
| Create PluginManifest | `domain/entities/plugin_manifest.py` | ⬜ | Validation |
| Create PluginRegistry | `application/services/plugin_registry.py` | ⬜ | Lifecycle management |
| Create permission enforcement | `application/services/plugin_permissions.py` | ⬜ | Checks |
| Create plugin routes | `presentation/api/v1/plugin_routes.py` | ⬜ | Load, unload, list plugins |

**Frozen APIs**: Plugin protocol

**Verification**: Plugin lifecycle, permission enforcement tests pass

### 1.8 Phase 7: Production Hardening (2-3 hours)

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Implement all stubbed items | All files | ⬜ | Remove NotImplementedError |
| Add error handling | All files | ⬜ | try/except/finally |
| Add structured logging | All files | ⬜ | JSON logs with context |
| Create health checks | All components | ⬜ | /health for all services |
| Add metrics collection | `infrastructure/metrics/` | ⬜ | Tool calls, latency, errors |
| Add rate limiting | `core/middleware/rate_limit.py` | ⬜ | Per user |
| Add input validation | All endpoints | ⬜ | Pydantic validation |
| Add PII redaction | Entry points | ⬜ | No logging of user data |
| Create unit tests | `tests/unit/` | ⬜ | 70% coverage target |
| Create integration tests | `tests/integration/` | ⬜ | Real DSPy + Ollama |
| Create E2E tests | `tests/e2e/` | ⬜ | Complete flows |

**Frozen APIs**: Complete system (v8.0.0)

**Verification**: All tests pass, coverage >70%, load test succeeds

---

## 2. Verification Steps

### 2.1 Code Quality

```bash
# Run all quality checks
cd /home/riju279/Documents/Code/XRIG/AgentX/agentx
ruff check . --fix
ruff format .
pyrefly check . --summarize-errors

# Frontend type check
cd /home/riju279/Documents/Code/XRIG/AgentX/frontend
npx tsc --noEmit
```

### 2.2 Phase Completion Checklist

For each phase (0-7):

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Unit tests
pytest tests/unit/ -v

# 3. Integration tests
pytest tests/integration/ -v

# 4. Coverage (Phase 7 only)
pytest --cov=agentx --cov-report=html

# 5. API documentation
# Verify all frozen APIs documented
```

### 2.3 API Freeze Verification

```bash
# After each phase, verify APIs frozen:
# 1. Check API documentation updated
grep -r "FROZEN" docs/api/

# 2. Check version tagged
git tag | grep "v[0-9]\.0\.0"

# 3. Check no breaking changes to frozen APIs
# Compare signatures with documentation
```

### 2.4 Dependency Verification

```bash
# Before starting Phase N:
# 1. Verify Phase N-1 complete
curl http://localhost:8000/health
grep "Phase N-1 Complete" docs/releases/

# 2. Verify required changes complete
openspec list --json | jq ".changes[] | select(.name | contains(\"C00\"))"

# 3. Verify frozen APIs available
python -c "from agentx.domain.entities import AgentSessionEntity; print('OK')"
```

### 2.5 Integration Tests

```bash
# Run integration tests for complete system (Phase 7)
pytest tests/integration/test_full_pipeline.py -v

# Run stress test
pytest tests/integration/test_load.py -v
```

---

## 3. Acceptance Criteria

### 3.1 Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| **All 8 phases defined** | Review specs.md | 8 phases with scope and deliverables |
| **API freezing rules documented** | Review specs.md | ≥3 rules documented |
| **Verification criteria complete** | Review specs.md | All 8 phases have tests |
| **Dependency graph established** | Review design.md | Linear 0→1→2→3→4→5→6→7 |
| **Health checks work** | `curl /health` | Returns 200 for all components |
| **Unit tests pass** | `pytest tests/unit/` | Zero failures |
| **Integration tests pass** | `pytest tests/integration/` | Zero failures |
| **Coverage target met** | `pytest --cov` | >70% in Phase 7 |

### 3.2 Non-Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| **Phase duration ≤3 hours** | Time tracking | Each phase ≤3 hours |
| **Health check latency** | `time curl /health` | <1 second |
| **Unit test execution** | `time pytest tests/unit/` | <5 minutes |
| **Integration test execution** | `time pytest tests/integration/` | <10 minutes |
| **Code quality** | `ruff check`, `ruff format` | Zero errors |
| **Type checking** | `pyrefly check` | Zero errors |
| **TypeScript compiles** | `npx tsc --noEmit` | Zero errors |

### 3.3 Integration Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| **C001 alignment** | File structure check | Clean Architecture layers match |
| **C002 alignment** | DTO usage | All DTOs follow Pydantic v2 patterns |
| **C003 integration** | Agent tests | DSPy agents work with LangGraph |
| **C004 integration** | Voice tests | Voice services integrated (Phase 7) |
| **C005 integration** | Memory tests | TemporalRAGService works |
| **C007 integration** | Frontend tests | LangGraph SDK, LoadExternalComponent |
| **C008 integration** | UI tests | Metaballs, voice nucleus, design tokens |
| **C009 integration** | Polish tests | Raycast minimalism applied |
| **LLD alignment** | Grep tests | 100% field name match |

---

## 4. Definition of Done

C006-release-plan is **complete** when:

- [ ] All 7 artifacts created (scan, extract, validate, proposal, specs, design, tasks)
- [ ] All 8 phases defined with scope and deliverables
- [ ] API freezing rules documented
- [ ] Verification criteria for each phase
- [ ] Dependency graph established (0→1→2→3→4→5→6→7)
- [ ] Integration with C001-C009 specifications
- [ ] All frozen APIs documented
- [ ] All verification criteria documented
- [ ] LLD alignment verified (100% match)
- [ ] Change → Phase mapping complete

**Implementation Complete** when (after applying all phases):

- [ ] Phase 0 complete (health check returns 200)
- [ ] Phase 1 complete (entities, repositories created)
- [ ] Phase 2 complete (agent returns calculator results)
- [ ] Phase 3 complete (UI descriptors, WebSocket working)
- [ ] Phase 4 complete (state machine transitions work)
- [ ] Phase 5 complete (memory storage, retrieval work)
- [ ] Phase 6 complete (plugin lifecycle works)
- [ ] Phase 7 complete (all tests pass, coverage >70%)
- [ ] All frozen APIs documented
- [ ] All verification criteria pass
- [ ] Code quality checks pass (ruff, pyrefly, tsc)
- [ ] Integration tests pass
- [ ] E2E tests pass

---

## 5. Rollback Plan

If a phase fails:

### 5.1 Identify Failure Point

```bash
# Check which test failed
pytest tests/unit/ -v

# Check service health
curl http://localhost:8000/health

# Check phase status
openspec status --change "c006-release-plan"
```

### 5.2 Rollback Steps

```bash
# 1. Revert to previous phase commit
git log --oneline | grep "Phase N"
git reset --hard <commit-hash>

# 2. Remove phase files
# (List from tasks.md section for failed phase)

# 3. Restart services
systemctl restart agentx

# 4. Verify previous phase still works
curl http://localhost:8000/health
pytest tests/integration/ -v
```

### 5.3 Recovery Actions

- **Re-run failed phase**: Start from beginning of phase tasks
- **Split phase**: If phase too large, split into sub-phases
- **Defer features**: Stub non-critical items with NotImplementedError
- **Add tests**: Add integration tests for problematic areas
- **Review dependencies**: Verify all frozen APIs still compatible

---

## 6. Phase Dependency Graph

```
Phase 0 (Server) ──────────────────────────────────────┐
                                                          │
Phase 1 (Domain) ──────────────────────────────────┐   │
                                                      │   │
Phase 2 (Agent) ──────────────────────────────┐   │   │
                                                  │   │   │
Phase 3 (UI + Frontend) ────────────────────┐   │   │   │
                                              │   │   │   │
Phase 4 (State + Polish) ─────────────────┐   │   │   │   │
                                          │   │   │   │   │
Phase 5 (Memory) ────────────────────┐   │   │   │   │   │
                                      │   │   │   │   │   │
Phase 6 (Plugins) ────────────────┐   │   │   │   │   │   │
                                  │   │   │   │   │   │   │
Phase 7 (Hardening) ──────────┐   │   │   │   │   │   │   │
                              │   │   │   │   │   │   │   │
Dependencies:                │   │   │   │   │   │   │   │
├─ C001-folder-structure      └───┴───┴───┴───┴───┴───┴───┘ (All phases)
├─ C002-data-contracts        └─────────┴─────────┴───────┘ (Phase 2+)
├─ C003-agent-pipeline        └─────────────┴─────────────┘ (Phase 2-4)
├─ C004-voice-streaming       └───────────────────────────┘ (Phase 7)
├─ C005-memory-rag            └─────────────────────┘ (Phase 5)
├─ C007-frontend-architecture └─────────────┴─────────────┘ (Phase 3-4)
├─ C008-organic-ui            └─────────────┴─────────────┘ (Phase 3-4)
└─ C009-ui-polish             └───────────────────────────┘ (Phase 4)
```

---

## 7. Change → Phase Mapping

| Change | Phases Enabled | Notes |
|--------|----------------|-------|
| **C001-folder-structure** | All phases (0-7) | Clean Architecture foundation |
| **C002-data-contracts** | Phase 2+ | DTOs required for API layer |
| **C003-agent-pipeline** | Phase 2-4 | DSPy agents, LangGraph, server-driven UI |
| **C004-voice-streaming** | Phase 7 | Voice services integration |
| **C005-memory-rag** | Phase 5 | Memory + RAG services |
| **C007-frontend-architecture** | Phase 3-4 | LangGraph SDK, LoadExternalComponent |
| **C008-organic-ui** | Phase 3-4 | Metaballs, voice nucleus, design tokens |
| **C009-ui-polish** | Phase 4 | Raycast minimalism, aesthetic fixes |

**Total Changes**: 9 (C001-C009)

---

## 8. Port Assignments

| Phase | Ports | Purpose |
|-------|-------|---------|
| **Phase 0** | 8000 | Main API server |
| **Phase 3** | 8016 | WebSocket streaming |
| **Phase 4** | 8015-8017 | Agent services |
| **Phase 5** | 8021-8022 | Memory services |
| **Phase 7** | All above | Complete system |

**Reserved Ports** (do not use):
- 8000-8014: Main application ports
- 8018-8020: C004 voice streaming
- 8080: SearXNG

---

## 9. Verification Checklist

Before marking C006-release-plan complete, verify:

- [x] All 7 artifacts created (scan, extract, validate, proposal, specs, design, tasks)
- [ ] All 8 phases defined with scope and deliverables
- [ ] API freezing rules documented
- [ ] Verification criteria for each phase
- [ ] Dependency graph established
- [ ] Integration with C001-C009 specifications
- [ ] LLD alignment verified (100% match)
- [ ] Frozen APIs documented
- [ ] Health check endpoints defined
- [ ] Unit test framework configured
- [ ] Integration test framework configured
- [ ] Coverage reporting enabled
- [ ] Rollback plan documented

---

## 10. Dependencies Unlocked

This change unlocks:

| Feature | Description |
|---------|-------------|
| **Phase 0 Implementation** | Can start building minimal server |
| **Phase 1 Implementation** | Can start building domain layer |
| **Phase 2-7 Implementation** | Can continue incremental delivery |
| **Parallel Development** | Multiple teams can work on different phases after API freezing |
| **Continuous Validation** | Each phase verified before completion |

---

**End of spec-factory pipeline**

**All 9 changes complete**: C001-C009, 63 artifacts total
