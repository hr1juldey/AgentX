# Proposal: c002-data-contracts

**Generated**: 2026-01-28
**Change**: c002-data-contracts
**Schema**: spec-factory v1

---

## Summary

Establish single source of truth for data contracts between backend (Pydantic v2) and frontend (Zod), aligning R014 implementations with locked LLD definitions. Fix field name mismatches (`id`→`descriptor_id`, `type`→`descriptor_type`) and type value mismatches (`"markdown"`→`"markdown_block"`).

---

## Motivation

### Problem Statement

R014 has field name mismatches between backend and frontend, scattered Pydantic models across service folders, and inconsistent type values with LLD. This causes API contract drift, type safety violations, and maintenance burden.

### Current State

- Backend uses `id`/`type` fields, LLD defines `descriptor_id`/`descriptor_type`
- Frontend correctly uses `descriptor_id`/`descriptor_type` (matches LLD)
- Type values: R014 uses `"markdown"`, LLD defines `MARKDOWN_BLOCK = "markdown_block"`
- Scattered schemas: `services/multihop_search/schemas.py` duplicates DTOs
- Type aliases instead of proper DTOs: `UIDescriptorResponse = UIDescriptor`

### Desired State

- All contracts follow LLD definitions exactly
- Pydantic v2 models in `application/dtos/` with field descriptions
- Zod schemas in `frontend/types/` match Pydantic models field-for-field
- Single source of truth: LLD → Pydantic → Zod

---

## Scope

### In Scope

- **UI Descriptor Contracts**: BaseUIDescriptor, 7 core descriptors
- **WebSocket Protocol**: All 15 message types and payloads
- **API DTOs**: Request/Response DTOs for all endpoints
- **Pydantic-Zod Synchronization**: Type mappings, validation rules

### Out of Scope

- Plugin descriptors (covered in plugin system spec)
- Agent state contracts (covered in C003-agent-pipeline)
- Voice streaming contracts (covered in C004-voice-streaming)

### Dependencies

| Change | Status | Required For |
|--------|--------|--------------|
| C001-folder-structure | ✅ Complete | Defines where DTOs and types live |

---

## Success Criteria

1. **Criterion 1**: All field names match LLD exactly
   - Measure: `grep -r "^\s*id:" agentx/ui/descriptors/` returns zero
   - Measure: `grep -r "descriptor_id:" agentx/ui/descriptors/` returns > 0

2. **Criterion 2**: All type values match LLD enum values
   - Measure: `grep -r '"markdown"' agentx/ui/descriptors/` returns zero
   - Measure: `grep -r '"markdown_block"' agentx/ui/descriptors/` returns > 0

3. **Criterion 3**: Frontend Zod schemas match backend Pydantic
   - Measure: Field name comparison test passes
   - Target: 100% field name alignment

4. **Criterion 4**: No scattered schemas in service folders
   - Measure: `find agentx/ -name "schemas.py"` returns zero
   - Target: All models in `application/dtos/`

---

## Implementation Approach

### High-Level Approach

1. **Phase 2.1** (from incremental release plan): Create UI descriptor contracts
   - Create `BaseUIDescriptor` with LLD-compliant fields
   - Create 7 core descriptor classes
   - Create `WebSocketMessage` and all payload classes

2. **Phase 2.2**: Create application DTOs
   - Request DTOs: `GenerateWidgetRequestDTO`, `SearchRequestDTO`, etc.
   - Response DTOs: Separate classes (not aliases)

3. **Frontend alignment**: Create Zod schemas
   - `BaseUIDescriptorSchema` matching Pydantic
   - `WebSocketMessageSchema` matching Pydantic
   - All 7 descriptor schemas

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Use LLD field names | Source of truth, avoids drift | Keep R014 names (violates LLD) |
| Separate DTOs | Clear validation layer | Type aliases (no separate validation) |
| Zod for frontend | Runtime type validation | TypeScript interfaces (no validation) |
| Remove extra widget types | LLD defines 7 core types | Keep 13 types (violates LLD) |

### Constraints

- **Ports**: 8015 (API), 8016 (WebSocket)
- **File size**: Max 150 lines per file
- **Imports**: Absolute only (CLAUDE_POLICY.md)
- **Locked definitions**: Must match LLD exactly

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking change to R014 | Medium | High | R014 is prototype, not production |
| Frontend-backend sync drift | Medium | Medium | Create validation tests for alignment |
| Enum value confusion | Low | Medium | Use constants file for shared values |

---

## Open Questions

1. **Should we support backward compatibility with `id`/`type` fields?**
   - Recommendation: No, R014 is prototype only
   - Alternative: Add migration guide for any existing consumers

2. **Should Zod schemas be generated or hand-written?**
   - Recommendation: Hand-written for now, consider code generation later
   - Alternative: Use tools like `pydantic-to-zod` or `openapi-zod-client`

---

**Next Artifact**: specs.md
