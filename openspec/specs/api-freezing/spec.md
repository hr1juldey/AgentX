# Spec: api-freezing

**File**: `specs/api-freezing/spec.md`

## 1.1 Purpose

Define the API freezing strategy that enables parallel development across phases while maintaining compatibility. Once a phase is complete, its APIs are frozen - no breaking changes allowed.

## 1.2 Scope

**In Scope**:
- API freeze rules (when to freeze, what to freeze)
- Breaking change policy (how to handle required changes)
- Versioning strategy (semantic versioning)
- Documentation requirements (API docs after freeze)

**Out of Scope**:
- Specific API definitions (covered by C001-C009)
- API documentation format (Swagger/OpenAPI)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-AF-001 | Frozen APIs MUST NOT change signatures | Must |
| FR-AF-002 | Frozen APIs MUST NOT break backward compatibility | Must |
| FR-AF-003 | Breaking changes MUST increment major version | Must |
| FR-AF-004 | API freeze MUST be documented in phase completion | Must |
| FR-AF-005 | Frontend widget names MUST match backend `push_ui_message()` calls | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-AF-001 | API documentation MUST be updated after freeze | Should |
| NFR-AF-002 | Breaking changes MUST be communicated | Should |

## 1.4 API Freezing Rules

**Locked from LLD** (incremental_release_plan.md:31-34):

```python
# API Freezing Rules:
# - Once a phase is complete, its APIs are frozen
# - Subsequent phases must use existing APIs
# - Breaking changes require new major version (v2.0)
# - Stubbed items raise NotImplementedError
```

### What Gets Frozen

| Category | Examples | Frozen When |
|----------|----------|-------------|
| **Entity Fields** | `UserEntity.user_id`, `MemoryEntity.content` | Phase 1 |
| **Repository Methods** | `MemoryRepository.store_memory()` | Phase 1 |
| **Pydantic Schemas** | `StoreMemoryCommand` fields | Phase 2 |
| **Zod Schemas** | `StoreMemoryCommandSchema` fields | Phase 2 |
| **Agent Signature** | `ReAct(question->answer)` | Phase 3 |
| **Voice API** | `POST /api/v1/voice/session` | Phase 4 |
| **RAG Interface** | `TemporalRAGService.search()` | Phase 5 |
| **Plugin Protocol** | `FastMCP tool()` decorator | Phase 6 |
| **Widget Names** | `push_ui_message("card", {...})` | Phase 7 |
| **Design Tokens** | `tokens.colors.void` | Phase 8 |

### Breaking Change Examples

| Change Type | Breaking? | Action |
|-------------|-----------|--------|
| Add optional field to Pydantic | No | Increment patch (v0.0.1) |
| Add required field to Pydantic | Yes | Increment major (v1.0.0) |
| Rename widget component | Yes | Increment major, update all calls |
| Change port assignment | Yes | Increment major, update docs |
| Add new widget type | No | Increment patch, add to ui.tsx |

## 1.5 Versioning Strategy

### Semantic Versioning

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes (incompatible API changes)
MINOR: New features (backward-compatible additions)
PATCH: Bug fixes (backward-compatible fixes)
```

### Examples

| Version | Change Example |
|---------|----------------|
| `0.1.0` | Phase 0-2 complete (backend MVP) |
| `0.2.0` | Phase 3-5 complete (agent + voice + memory) |
| `0.3.0` | Phase 6 complete (plugins) |
| `0.4.0` | Phase 7 complete (frontend architecture) |
| `0.5.0` | Phase 8 complete (organic UI) |
| `0.6.0` | Phase 9 complete (UI polish) |
| `1.0.0` | Phase 10 complete (production release) |
| `1.1.0` | Add new widget type |
| `2.0.0` | Breaking change to agent signature |

## 1.6 Phase Completion Checklist

For each phase, before marking complete:

- [ ] All phase deliverables implemented
- [ ] All tests passing
- [ ] Health check endpoint responding
- [ ] APIs documented (list of frozen endpoints/schemas)
- [ ] No breaking changes to previous phases
- [ ] Code review approved
- [ ] Phase time = 2-3 hours (alert if exceeded)

## 1.7 API Freeze Documentation Template

```markdown
# Phase N: API Freeze Document

## Frozen Entities
- EntityName: {field1: type, field2: type}

## Frozen Repositories
- RepositoryName.method_name(args) -> return_type

## Frozen Pydantic Schemas
- SchemaName: {field1: type, field2: type}

## Frozen Zod Schemas
- SchemaNameSchema: {field1: z.type(), field2: z.type()}

## Frozen Endpoints
- METHOD /path: Request -> Response

## Frozen Widget Names
- "widgetName": ComponentName

## Version
- v{major}.{minor}.{patch}

## Freeze Date
- YYYY-MM-DD
```

## 1.8 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-AF-001 | APIs frozen when phase marked complete | Documentation review |
| BR-AF-002 | No signature changes after freeze | Code review |
| BR-AF-003 | Breaking changes increment major version | Version check |
| BR-AF-004 | Widget names must match backend calls | Integration test |

## 1.9 Acceptance Criteria

- [ ] API freezing rules documented
- [ ] Breaking change policy defined
- [ ] Versioning strategy established
- [ ] Phase completion checklist created
- [ ] API freeze template provided
- [ ] All phases (0-10) have freeze documentation

## 1.10 Frontend-Specific Rules (from C007)

### Widget Name Freezing

| Rule | Description |
|------|-------------|
| **Widget Names** | Once defined in `ui.tsx`, names are frozen |
| **Props Interface** | Component props must match backend `push_ui_message()` |
| **Design Tokens** | Once defined, token values are frozen |

### Example

```python
# Backend: Frozen in Phase 7
push_ui_message("card", {"title": "...", "content": "..."})
```

```typescript
// Frontend: Must match
export default {
  card: CardComponent,  // Frozen name: "card"
};

interface CardProps {
  title: string;       // Frozen prop
  content: string;     // Frozen prop
}
```

---

**Related Specs**:
- `specs/incremental-delivery/spec.md` - Phase definitions
- C001-C009 - Individual phase specifications with frozen APIs
