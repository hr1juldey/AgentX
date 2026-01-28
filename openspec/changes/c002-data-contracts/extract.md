# Extract Artifact: c002-data-contracts

**Generated**: 2026-01-28
**Change**: c002-data-contracts
**Schema**: spec-factory v1

---

## 1. Pattern Catalog

### 1.1 Architectural Patterns

| Pattern | Source | Description | Apply? |
|---------|--------|-------------|--------|
| Single Source of Truth | LLD | LLD defines all contracts, code implements | ✅ |
| Pydantic v2 Syntax | LLD | `str \| None` instead of `Optional[str]` | ✅ |
| Zod for Frontend | Best Practice | Runtime type validation matching Pydantic | ✅ |
| Field Descriptions | LLD | All fields have `Field(..., description=...)` | ✅ |
| Enum Validation | LLD | Closed set of types via Literal or Enum | ✅ |
| DTO Separation | mimicus | Separate Request/Response DTOs from entities | ✅ |

### 1.2 Code Structure Patterns

| Pattern | Backend Example | Frontend Example | Apply? |
|---------|-----------------|-------------------|--------|
| Descriptor base class | `BaseUIDescriptor` | Zod schema base | ✅ |
| Type-safe enums | `UIDescriptorType(str, Enum)` | `z.enum([...])` | ✅ |
| Request DTOs | `GenerateWidgetRequest` | `GenerateWidgetRequestSchema` | ✅ |
| Response DTOs | `WidgetResponseDTO` | `WidgetResponseSchema` | ✅ |
| WebSocket messages | `WebSocketMessage` | `WebSocketMessageSchema` | ✅ |

### 1.3 Naming Patterns (to Avoid from R014)

| R014 Name | Why Avoid | Alternative |
|-----------|-----------|-------------|
| `id` field | Conflicts with Python built-in, LLD uses `descriptor_id` | `descriptor_id` |
| `type` field | Python built-in, LLD uses `descriptor_type` | `descriptor_type` |
| `"markdown"` value | LLD enum is `MARKDOWN_BLOCK = "markdown_block"` | `"markdown_block"` |
| Type alias (`UIDescriptorResponse = UIDescriptor`) | No separate validation layer | Separate `UIDescriptorResponseDTO` class |
| Scattered `schemas.py` | Duplication, hard to maintain | Consolidate to `application/dtos/` |

---

## 2. Specification Drafts

### 2.1 Draft: ui-descriptor-contracts Spec

**Purpose**: Define UI descriptor data contracts with Pydantic v2 ↔ Zod alignment.

**Scope**:
- **In scope**: BaseUIDescriptor, 7 core descriptors, WebSocket messages
- **Out of scope**: Plugin descriptors, agent state (covered in other specs)

**Locked from LLD**:
```python
# From ui_descriptor_contract.md:33-46, 48-66
class UIDescriptorType(str, Enum):
    MARKDOWN_BLOCK = "markdown_block"
    CARD = "card"
    FORM = "form"
    PROGRESS = "progress"
    ACTION = "action"
    CONFIRMATION = "confirmation"
    VOICE = "voice"

class BaseUIDescriptor(BaseModel):
    descriptor_id: str
    descriptor_type: UIDescriptorType
    display_name: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    dismissible: bool = True
```

**Requirements**:
1. All descriptors SHALL inherit from `BaseUIDescriptor`
2. All descriptors SHALL use `descriptor_id` (not `id`)
3. All descriptors SHALL use `descriptor_type` (not `type`)
4. Type values SHALL match LLD enum values exactly
5. All fields SHALL have descriptions in Pydantic `Field()`
6. Frontend Zod schemas SHALL match Pydantic models field-for-field

**Acceptance Criteria**:
- [ ] Backend `BaseUIDescriptor` exists with correct fields
- [ ] Frontend `BaseUIDescriptorSchema` matches backend exactly
- [ ] No `id` or `type` fields in any descriptor
- [ ] All type values use LLD enum format (`markdown_block`, not `markdown`)

---

### 2.2 Draft: websocket-protocol Spec

**Purpose**: Define WebSocket message contracts for agent communication.

**Scope**:
- **In scope**: All WebSocket message types and payloads
- **Out of scope**: REST API contracts (separate spec)

**Locked from LLD**:
```python
# From ui_descriptor_contract.md:335-382
class WebSocketMessageType(str, Enum):
    TOKEN = "token"
    REASONING_STEP = "reasoning_step"
    TOOL_CALL = "tool_call"
    DESCRIPTOR_CREATE = "descriptor_create"
    DESCRIPTOR_UPDATE = "descriptor_update"
    ERROR = "error"
    # ... (all 15 types)

class WebSocketMessage(BaseModel):
    message_type: WebSocketMessageType
    timestamp: datetime
    session_id: str
    data: Dict[str, Any]
    message_id: Optional[str]
    correlation_id: Optional[str]
```

**Requirements**:
1. All messages SHALL inherit from `WebSocketMessage`
2. Message types SHALL be closed enum (no arbitrary strings)
3. All payloads SHALL be Pydantic models with validation
4. Frontend SHALL have matching Zod schemas for all messages

**Acceptance Criteria**:
- [ ] All 15 message types defined in enum
- [ ] Payload classes for each message type
- [ ] Frontend Zod schemas match exactly

---

### 2.3 Draft: pydantic-zod-sync Spec

**Purpose**: Establish single source of truth for data contracts.

**Scope**:
- **In scope**: Mapping rules, validation synchronization, type conversion
- **Out of scope**: Implementation details (covered in design)

**Requirements**:
1. Backend Pydantic models SHALL be source of truth
2. Frontend Zod schemas SHALL be generated/validated against backend
3. Field names SHALL match exactly (`descriptor_id`, not `id`)
4. Enum values SHALL match exactly (`markdown_block`, not `markdown`)
5. Optional fields SHALL use `str | None` (Pydantic v2) and `z.string().optional()` (Zod)

**Acceptance Criteria**:
- [ ] Mapping document exists (Pydantic → Zod)
- [ ] Type validation tests pass both sides
- [ ] Zero field name mismatches
- [ ] Zero enum value mismatches

---

## 3. API Contracts

### 3.1 REST Endpoints

| Method | Path | Request | Response | Status Codes |
|--------|------|---------|----------|--------------|
| POST | `/api/v1/widgets/generate` | `GenerateWidgetRequestDTO` | `UIDescriptorResponseDTO` | 200, 400, 500 |
| POST | `/api/v1/search` | `SearchRequestDTO` | `SearchResultResponseDTO` | 200, 404, 500 |

### 3.2 WebSocket Channels

| Channel | Message Types | Schema |
|---------|--------------|--------|
| `/ws/agent` | All 15 WebSocketMessageType | `WebSocketMessage` |
| `/ws/widgets` | DESCRIPTOR_* messages | `DescriptorCreatePayload`, etc. |

### 3.3 Port Assignments

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| AgentX API | 8015 | HTTP | REST API |
| WebSocket | 8016 | WS | Agent + Widget streaming |

---

## 4. Data Model Mappings

### 4.1 Pydantic → Zod Mappings

| Pydantic Model | Zod Type | Notes |
|----------------|----------|-------|
| `str` | `z.string()` | Direct mapping |
| `str | None` | `z.string().optional()` | Optional |
| `int` | `z.number()` | Integer |
| `float` | `z.number()` | Number |
| `bool` | `z.boolean()` | Boolean |
| `datetime` | `z.string().datetime()` | ISO format |
| `Dict[str, Any]` | `z.record(z.any())` | Flexible dict |
| `List[str]` | `z.array(z.string())` | String array |
| `Literal["a", "b"]` | `z.enum(["a", "b"])` | Enum |

### 4.2 Field Name Mappings (Critical Fixes)

| LLD/Correct | R014 Backend (Wrong) | Fix Required |
|-------------|---------------------|--------------|
| `descriptor_id` | `id` | Change to `descriptor_id` |
| `descriptor_type` | `type` | Change to `descriptor_type` |
| `display_name` | (missing) | Add field |
| `MARKDOWN_BLOCK` | `"markdown"` | Change value to `"markdown_block"` |

### 4.3 Shared Types (Backend = Frontend)

```python
# Backend (Pydantic v2)
class BaseUIDescriptor(BaseModel):
    descriptor_id: str
    descriptor_type: UIDescriptorType
    display_name: Optional[str]
    metadata: Dict[str, Any]
```

```typescript
// Frontend (Zod)
const BaseUIDescriptorSchema = z.object({
  descriptor_id: z.string(),
  descriptor_type: z.enum(["markdown_block", "card", "form", ...]),
  display_name: z.string().optional(),
  metadata: z.record(z.any()),
});
```

---

## 5. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| C001-folder-structure | Depends on | C001 defines where DTOs and types live |
| C003-agent-pipeline | Depends on | Agent pipeline uses WebSocket contracts |
| C004-voice-streaming | Depends on | Voice streaming uses descriptor contracts |

**Unlocks**: C002 enables C003, C004, C005 by providing API contracts

---

**Next Artifact**: validate.md
