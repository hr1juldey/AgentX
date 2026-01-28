# Proposal: c001-folder-structure

**Generated**: 2026-01-28
**Change**: c001-folder-structure
**Schema**: spec-factory v1

---

## Summary

Establish the foundational folder structure for Real AgentX v0.1 backend and frontend, following Clean Architecture principles from mimicus and incorporating proven patterns from R014. This creates the organizational framework that all subsequent features (C002-C006) will build upon.

---

## Motivation

### Problem Statement

R014 prototype has 264 Python files with scattered data models, hardcoded values, and 21 agent classes causing complexity explosion. The current structure lacks clear separation of concerns, making it difficult to maintain and extend. Without a locked folder structure, future features will repeat these mistakes.

### Current State

- R014: `services/` contains 189 files, `models.py` and `schemas.py` scattered across folders
- R014: 21 agent classes in `widget_spawner/` alone
- R014: Hardcoded IPs and model names throughout code
- No consistent file placement rules
- Mimicus has proven Clean Architecture but we need to adapt it for AgentX

### Desired State

- Clear 7-layer Clean Architecture: core/, domain/, infrastructure/, agent/, ui/, application/, presentation/
- All data models consolidated to `domain/entities/` and `application/dtos/`
- Consistent naming conventions enforced
- All files < 150 lines (100 executable + 50 overhead)
- Absolute imports only (CLAUDE_POLICY.md compliance)

---

## Scope

### In Scope

- **Backend folder structure**: 7-layer Clean Architecture at `/home/riju279/Documents/Code/XRIG/AgentX/agentx/`
  - `core/` - Configuration and dependency injection
  - `domain/` - Business entities, repositories, services
  - `infrastructure/` - External adapters (database, HTTP, storage)
  - `agent/` - DSPy agents, tools, signatures
  - `ui/` - UI descriptors and WebSocket protocols
  - `application/` - Use cases, DTOs, mappers
  - `presentation/` - FastAPI routes
- **Frontend folder structure**: Next.js 15 App Router at `/home/riju279/Documents/Code/XRIG/AgentX/frontend/`
  - `components/` - React components (ui/, descriptors/, layout/)
  - `store/` - Zustand stores with atomic state pattern
  - `types/` - TypeScript type definitions
  - `hooks/` - Custom React hooks
- **File naming conventions**: Rules for where files belong (no `models.py` in services)
- **Import rules**: Absolute imports only

### Out of Scope

- Runtime behavior (see C003-agent-pipeline, C004-voice-streaming)
- API contracts (see C002-data-contracts)
- Data model definitions (locked in LLD, this is just placement)
- WebSocket protocol (see C003-agent-pipeline)

### Dependencies

None. C001 is the foundation spec that enables C002-C006.

---

## Success Criteria

1. **Criterion 1**: All 7 backend layers exist with correct structure
   - Measure: Directory check and file listing
   - Target: All directories present, README.md in each layer explaining purpose

2. **Criterion 2**: All data models follow placement rules
   - Measure: Grep for `models.py` and `schemas.py` in service folders
   - Target: Zero instances (all consolidated to domain/ or application/dtos/)

3. **Criterion 3**: All imports are absolute paths
   - Measure: `grep -r "from \.\." agentx/`
   - Target: Zero matches

4. **Criterion 4**: All files pass size limits
   - Measure: `find agentx/ -name "*.py" -exec wc -l {} + | awk '$1 > 150'`
   - Target: Zero files exceed 150 lines

5. **Criterion 5**: All code passes quality checks
   - Measure: `ruff check --fix`, `ruff format`, `pyrefly check --summarize-errors`
   - Target: All commands pass with zero errors

---

## Implementation Approach

### High-Level Approach

1. **Phase 0** (Foundation): Create `agentx/` root with `core/`, `main.py`, `.env.example`
2. **Phase 1** (Domain + Infrastructure): Create `domain/` entities/repositories, `infrastructure/` adapters
3. **Phase 2** (Main Agent): Create `agent/` layer with DSPy signatures and tools
4. **Phase 3** (UI + Streaming): Create `ui/` descriptors and WebSocket protocols
5. **Phase 4** (State Machines): Create `agent/langgraph/` with backend/frontend state machines
6. **Phase 5** (Memory + RAG): Create memory services and RAG agents
7. **Phase 6** (Plugins): Create `plugin/` layer with interface and registry
8. **Phase 7** (Hardening): Add `core/middleware/`, `monitoring/`, `tests/`

Frontend structure created in parallel with backend Phase 0-4.

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| 7 layers vs 5 layers | Mimicus has 5, but AgentX needs `agent/` and `ui/` layers for DSPy and UI descriptors | 5 layers (mimicus), 6 layers (merge agent/ into domain/) |
| `agent/` as separate layer | DSPy agents don't fit cleanly into domain/ or application/ | Merge into domain/ (too big), merge into application/ (wrong concern) |
| `ui/` as separate layer | UI descriptors and WebSocket protocols are unique concern | Merge into domain/ (UI is not domain logic), merge into application/ (needs persistence) |
| Absolute imports only | CLAUDE_POLICY.md requirement, proven by R014 | Relative imports (violates policy) |
| Atomic state pattern | Proven by R014 to prevent cascade re-renders | Global store (re-renders all widgets) |

### Constraints

- **Ports**: Use 8015+ (avoid 8000-8014) - applies to later phases
- **File size**: Max 100 lines executable + 50 overhead
- **Imports**: Absolute only (CLAUDE_POLICY.md)
- **Locked definitions**: All entities from domain_model.md must be used verbatim
- **No relative imports**: `from .` or `from ..` is forbidden

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| 7 layers too complex | Low | Medium | Document each layer clearly with README.md |
| `agent/` layer confuses developers | Medium | Medium | Clear guidelines: DSPy agents go here, not in domain/ |
| File splitting creates too many files | Low | Low | Use 150-line limit (vs 100-line in CLAUDE_POLICY.md) |
| Frontend structure diverges from backend | Medium | Low | Align naming: `descriptors/` maps to `ui/descriptors/` |
| Phase dependencies cause delays | Medium | Medium | C002 can proceed in parallel after Phase 1 completes |

---

## Open Questions

1. **Should frontend `agentx/` be called `backend/`?**
   - Recommendation: Keep `agentx/` for clarity (it's the backend of AgentX)
   - Alternative: `backend/` is more generic

2. **Should `infrastructure/` be split into `database/` and `external/`?**
   - Recommendation: Yes (mimicus does this)
   - File structure: `infrastructure/database/` for adapters, `infrastructure/external/` for HTTP/API

3. **Should tests be in `agentx/tests/` or project root `tests/`?**
   - Recommendation: `agentx/tests/` for co-location
   - Alternative: `/home/riju279/Documents/Code/XRIG/AgentX/tests/` for project-wide tests

---

**Next Artifact**: specs.md
