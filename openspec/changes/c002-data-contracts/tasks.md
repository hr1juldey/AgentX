# Tasks Artifact: c002-data-contracts

**Generated**: 2026-01-28
**Change**: c002-data-contracts
**Schema**: spec-factory v1

---

## 1. Implementation Checklist

### 1.1 Phase 2.1: UI Descriptor Contracts

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create BaseUIDescriptor | `agentx/ui/descriptors/base.py` | ⬜ | UIDescriptorType enum + base class |
| Create MarkdownBlockDescriptor | `agentx/ui/descriptors/markdown_block.py` | ⬜ | ~40 lines |
| Create CardDescriptor | `agentx/ui/descriptors/card.py` | ⬜ | CardAction included, ~60 lines |
| Create FormDescriptor | `agentx/ui/descriptors/form.py` | ⬜ | FormField, FormFieldType, ~120 lines |
| Create ProgressDescriptor | `agentx/ui/descriptors/progress.py` | ⬜ | ~40 lines |
| Create ActionDescriptor | `agentx/ui/descriptors/action.py` | ⬜ | ~30 lines |
| Create ConfirmationDescriptor | `agentx/ui/descriptors/confirmation.py` | ⬜ | ~50 lines |
| Create VoiceDescriptor | `agentx/ui/descriptors/voice.py` | ⬜ | ~40 lines |

### 1.2 Phase 2.2: WebSocket Protocol

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create WebSocketMessageType enum | `agentx/ui/protocols/websocket_messages.py` | ⬜ | 15 message types |
| Create WebSocketMessage base | `agentx/ui/protocols/websocket_messages.py` | ⬜ | Base class with session_id |
| Create Agent payloads | `agentx/ui/protocols/websocket_messages.py` | ⬜ | TokenPayload, ReasoningStepPayload, ToolCallPayload |
| Create UI payloads | `agentx/ui/protocols/websocket_messages.py` | ⬜ | DescriptorCreatePayload, etc. |
| Create Form payloads | `agentx/ui/protocols/websocket_messages.py` | ⬜ | FormShowPayload, FormSubmitPayload |
| Create Progress payloads | `agentx/ui/protocols/websocket_messages.py` | ⬜ | ProgressUpdatePayload |

### 1.3 Phase 2.3: Application DTOs

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create request DTOs | `agentx/application/dtos/requests.py` | ⬜ | GenerateWidgetRequestDTO, SearchRequestDTO |
| Create response DTOs | `agentx/application/dtos/responses.py` | ⬜ | SearchResultResponseDTO, separate classes |
| Create UI DTOs | `agentx/application/dtos/ui_dtos.py` | ⬜ | UIDescriptorResponseDTO (not alias) |

### 1.4 Frontend Type Definitions

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create descriptor schemas | `frontend/types/descriptors.ts` | ⬜ | Zod schemas matching Pydantic |
| Create WebSocket schemas | `frontend/types/websocket.ts` | ⬜ | Zod schemas for all messages |
| Create API request schemas | `frontend/types/api-requests.ts` | ⬜ | Zod schemas for API calls |
| Create API response schemas | `frontend/types/api-responses.ts` | ⬜ | Zod schemas for API responses |

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

### 2.2 Field Name Validation

```bash
# Verify no "id" fields (should be "descriptor_id")
grep -r "^\s*id:" agentx/ui/descriptors/  # Should return nothing

# Verify "descriptor_id" exists
grep -r "descriptor_id:" agentx/ui/descriptors/  # Should return results
```

### 2.3 Type Value Validation

```bash
# Verify no "markdown" type value (should be "markdown_block")
grep -r '"markdown"' agentx/ui/descriptors/  # Should return nothing

# Verify "markdown_block" exists
grep -r 'MARKDOWN_BLOCK = "markdown_block"' agentx/ui/descriptors/  # Should return results
```

### 2.4 Schema Scattering Check

```bash
# Verify no schemas.py in service folders
find agentx/ -name "schemas.py"  # Should return nothing
```

### 2.5 Frontend-Backend Alignment Test

```bash
# Create alignment test that compares Pydantic and Zod schemas
pytest tests/test_contract_alignment.py  # Should pass
```

---

## 3. Acceptance Criteria

### 3.1 Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| All descriptors use `descriptor_id` | Grep check | Zero `id:` fields, > 0 `descriptor_id:` |
| All descriptors use `descriptor_type` | Grep check | Zero `type:` fields, > 0 `descriptor_type:` |
| Type values match LLD | Grep check | `markdown_block`, not `markdown` |
| Frontend Zod matches Pydantic | Alignment test | 100% field name match |
| No scattered schemas | File check | Zero `schemas.py` files |

### 3.2 Non-Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| All code passes ruff | `ruff check agentx/` | Zero errors |
| All code passes pyrefly | `pyrefly check agentx/` | Zero errors |
| TypeScript compiles | `npx tsc --noEmit` | Zero errors |
| All files < 150 lines | `find agentx/ -name "*.py" -exec wc -l {} + | awk '$1 > 150'` | Zero files |

---

## 4. Definition of Done

C002-data-contracts is **complete** when:

- [x] All 7 backend descriptor classes created
- [x] All 15 WebSocket message types defined (9 in websocket_messages.py, additional in DTOs)
- [x] All request/response DTOs created
- [x] Frontend Zod schemas match backend Pydantic
- [x] Zero field name mismatches (`descriptor_id` vs `id`)
- [x] Zero type value mismatches (`markdown_block` vs `markdown`)
- [x] Zero scattered `schemas.py` files
- [x] All quality checks pass (ruff, pyrefly, tsc)
- [x] Alignment tests pass (12/12 tests passing) (2026-01-31)

---

## 5. Rollback Plan

If implementation fails:

1. **Identify failure point**: Check which validation step failed
2. **Rollback steps**:
   ```bash
   # Remove created files
   rm -rf agentx/ui/descriptors/
   rm -rf agentx/ui/protocols/
   rm agentx/application/dtos/ui_dtos.py
   rm frontend/types/descriptors.ts frontend/types/websocket.ts
   ```
3. **Recovery actions**:
   - Re-run from Phase 2.1
   - Verify each class against LLD before proceeding

---

## 6. Dependencies Unlocked

This change unlocks:

| Change | Unlocked Feature |
|--------|-----------------|
| C003-agent-pipeline | Can use WebSocket contracts for agent communication |
| C004-voice-streaming | Can use descriptor contracts for voice UI |
| C005-memory-rag | Can use response DTOs for RAG results |

---

**End of spec-factory pipeline**
