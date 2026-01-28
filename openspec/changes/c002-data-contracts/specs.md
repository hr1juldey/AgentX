# Specs Artifact: c002-data-contracts

**Generated**: 2026-01-28
**Change**: c002-data-contracts
**Schema**: spec-factory v1

---

## 1. Spec: ui-descriptor-contracts

**File**: `specs/ui-descriptor-contracts/spec.md`

**Purpose**: Define UI descriptor data contracts with Pydantic v2 ↔ Zod alignment, following locked LLD definitions.

**Key Requirements**:
- All descriptors use `descriptor_id` (not `id`)
- All descriptors use `descriptor_type` (not `type`)
- Type values match LLD enum: `markdown_block`, `card`, `form`, `progress`, `action`, `confirmation`, `voice`
- Frontend Zod schemas match Pydantic exactly

**Acceptance Criteria**:
- [ ] BaseUIDescriptor with correct fields
- [ ] All 7 descriptor types implemented
- [ ] Frontend Zod schemas match backend

---

## 2. Spec: websocket-protocol

**File**: `specs/websocket-protocol/spec.md`

**Purpose**: Define WebSocket message contracts for agent and UI communication.

**Key Requirements**:
- 15 message types: TOKEN, REASONING_STEP, TOOL_CALL, DESCRIPTOR_CREATE, DESCRIPTOR_UPDATE, DESCRIPTOR_DISMISS, ERROR, WARNING, INFO, SESSION_PAUSE, SESSION_RESUME, SESSION_CLOSE, FORM_SHOW, FORM_SUBMIT, FORM_VALIDATE, PROGRESS_START, PROGRESS_UPDATE, PROGRESS_COMPLETE
- All messages inherit from WebSocketMessage base class
- Payload classes for each message type

**Acceptance Criteria**:
- [ ] All 15 message types defined
- [ ] Payload classes with validation
- [ ] Frontend Zod schemas match backend

---

## 3. Spec: pydantic-zod-sync

**File**: `specs/pydantic-zod-sync/spec.md`

**Purpose**: Establish single source of truth mapping Pydantic v2 to Zod.

**Key Requirements**:
- Backend Pydantic is source of truth
- Frontend Zod schemas match field names exactly
- Optional fields: `str | None` ↔ `z.string().optional()`
- Enum values match exactly between Pydantic Literal and Zod enum

**Acceptance Criteria**:
- [ ] Mapping documentation exists
- [ ] Type validation tests pass both sides
- [ ] Zero field name mismatches

---

## 4. Cross-Domain Contracts

### 4.1 Shared Type Mappings

| Pydantic v2 | Zod | Location |
|-------------|-----|----------|
| `str` | `z.string()` | types/descriptors.ts |
| `str \| None` | `z.string().optional()` | types/descriptors.ts |
| `int` | `z.number()` | types/descriptors.ts |
| `float` | `z.number()` | types/descriptors.ts |
| `bool` | `z.boolean()` | types/descriptors.ts |
| `datetime` | `z.string().datetime()` | types/descriptors.ts |
| `Dict[str, Any]` | `z.record(z.any())` | types/descriptors.ts |
| `Literal["a", "b"]` | `z.enum(["a", "b"])` | types/descriptors.ts |

### 4.2 Critical Field Name Corrections

| Wrong (R014) | Correct (LLD) | Location |
|---------------|---------------|----------|
| `id` | `descriptor_id` | All descriptors |
| `type` | `descriptor_type` | All descriptors |
| `"markdown"` | `"markdown_block"` | Type enum value |

### 4.3 Integration Points

| Backend Domain | Frontend Domain | Interface |
|----------------|-----------------|-----------|
| `ui/descriptors/*.py` | `types/descriptors.ts` | UI descriptor types |
| `ui/protocols/websocket_messages.py` | `types/websocket.ts` | WebSocket protocol |
| `application/dtos/*.py` | `types/api-*.ts` | REST API contracts |

---

**Next Artifact**: design.md
