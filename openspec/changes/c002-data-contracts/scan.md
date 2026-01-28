# Scan Artifact: c002-data-contracts

**Generated**: 2026-01-28
**Change**: c002-data-contracts
**Schema**: spec-factory v1

---

## 1. LLD Synthesis

### 1.1 Relevant LLD Documents

| Document | Path | Relevance |
|----------|------|-----------|
| UI Descriptor Contract | `/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/ui_descriptor_contract.md` | Locked UI descriptor definitions |
| Domain Model | `/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/domain_model.md` | Entity definitions with locked types |
| LLD Master | `/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/LLD.md` | Document map and architecture |

### 1.2 Locked Definitions from LLD

#### UIDescriptorType Enum (Locked)

```python
# From ui_descriptor_contract.md:33-46
class UIDescriptorType(str, Enum):
    MARKDOWN_BLOCK = "markdown_block"  # Note: R014 uses "markdown"
    CARD = "card"
    FORM = "form"
    PROGRESS = "progress"
    ACTION = "action"
    CONFIRMATION = "confirmation"
    VOICE = "voice"
```

#### BaseUIDescriptor (Locked)

```python
# From ui_descriptor_contract.md:48-66
class BaseUIDescriptor(BaseModel):
    descriptor_id: str          # R014 uses "id"
    descriptor_type: UIDescriptorType  # R014 uses "type"
    display_name: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    dismissible: bool = True
```

#### WebSocketMessageType Enum (Locked)

```python
# From ui_descriptor_contract.md:335-371
class WebSocketMessageType(str, Enum):
    # Agent messages
    TOKEN = "token"
    REASONING_STEP = "reasoning_step"
    TOOL_CALL = "tool_call"
    STATUS_UPDATE = "status_update"

    # UI messages
    DESCRIPTOR_CREATE = "descriptor_create"
    DESCRIPTOR_UPDATE = "descriptor_update"
    DESCRIPTOR_DISMISS = "descriptor_dismiss"

    # System messages
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
```

#### Entity Field Types (Locked from domain_model.md)

| Entity | Field | Type | Notes |
|--------|-------|------|-------|
| AgentSessionEntity | session_id | UUID | Not str |
| AgentSessionEntity | user_id | str | SHA-256 hash |
| AgentSessionEntity | state | SessionState | Enum |
| UIComponentEntity | component_id | UUID | Not str |
| UIComponentEntity | component_type | UIComponentType | Enum |

---

## 2. Codebase Exploration (opsx:explore)

### 2.1 Exploration Topics

```
1. R014 backend Pydantic models at /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/
2. R014 frontend TypeScript types at /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/frontend/
3. LLD ui_descriptor_contract.md for locked definitions
```

### 2.2 File Inventory

#### Backend Files (R014)

| File | Lines | Purpose |
|------|-------|---------|
| `domain/entities/ui_descriptor.py` | 53 | Domain entity (WRONG field names!) |
| `application/dtos/requests.py` | 84 | Request DTOs (Pydantic v2 syntax) |
| `application/dtos/responses.py` | 38 | Response DTOs (uses domain entity alias) |
| `services/multihop_search/schemas.py` | 79 | ⚠️ SCATTERED Pydantic models (anti-pattern) |

#### Frontend Files (R014)

| File | Lines | Purpose |
|------|-------|---------|
| `types/widget-types.ts` | 213 | UI descriptor interfaces (has field name mismatches) |
| `store/widget-store.ts` | 312 | Atomic state pattern (correct structure) |
| `store/network-store.ts` | 184 | WebSocket/API health store |
| `store/ui-store.ts` | ~100 | UI state management |

---

## 3. Patterns Discovered

### 3.1 Architectural Patterns

**From LLD**:
- Single source of truth: LLD defines all descriptor contracts
- Pydantic v2 syntax: `str | None` instead of `Optional[str]`
- Field descriptions: All fields have `Field(..., description=...)`
- Enum validation: Closed set of descriptor types, widget types

**From R014**:
- Good: Pydantic v2 syntax used correctly in DTOs
- Good: Frontend uses `descriptor_id`/`descriptor_type` (matches LLD)
- Bad: Backend uses `id`/`type` (MISMATCH with LLD!)
- Bad: Scattered schemas.py in service folders (anti-pattern)

### 3.2 Code Patterns

| Pattern | Backend | Frontend |
|---------|---------|----------|
| Field naming (LLD) | `descriptor_id`, `descriptor_type` | `descriptor_id`, `descriptor_type` |
| Field naming (R014) | `id`, `type` (WRONG!) | `descriptor_id`, `descriptor_type` (correct) |
| Type values (LLD) | `markdown_block` | `markdown_block` |
| Type values (R014) | `markdown` (WRONG!) | `markdown` (needs fix) |
| Optional fields | `str | None` | `string \| undefined` |

### 3.3 Anti-Patterns to Avoid

**From R014**:
- ❌ Field name mismatch: Backend `id`/`type` vs LLD `descriptor_id`/`descriptor_type`
- ❌ Type value mismatch: `markdown` vs LLD `markdown_block`
- ❌ Scattered schemas: `services/multihop_search/schemas.py` (79 lines of duplicate models)
- ❌ Type alias instead of proper DTO: `UIDescriptorResponse = UIDescriptor` (no separate validation)

---

## 4. Reference Analysis

### 4.1 LLD Patterns (Source of Truth)

| Concept | LLD Definition | R014 Current | Required Fix |
|---------|----------------|--------------|--------------|
| Descriptor ID field | `descriptor_id: str` | `id: str` | Change to `descriptor_id` |
| Descriptor type field | `descriptor_type: UIDescriptorType` | `type: Literal[...]` | Change to `descriptor_type` |
| Descriptor type value | `MARKDOWN_BLOCK = "markdown_block"` | `"markdown"` | Change to `"markdown_block"` |
| Widget type enum | `UIComponentType` (7 types) | `WidgetType` (13 types) | Align to 7 core types |

### 4.2 R014 Reference (What to Avoid)

| Concept | R014 Approach | Improved Approach |
|---------|---------------|-------------------|
| Backend field names | `id`, `type` | `descriptor_id`, `descriptor_type` (matches LLD) |
| Type values | `"markdown"`, `"card"` | `"markdown_block"`, `"card"` (matches LLD enum) |
| DTO reuse | `UIDescriptorResponse = UIDescriptor` (alias) | Separate `UIDescriptorResponseDTO` class |
| Model location | Scattered in service folders | Consolidated to `application/dtos/` |

---

## 5. Key Files for This Change

### LLD Documents (Source of Truth)

```
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/ui_descriptor_contract.md
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/domain_model.md
```

### R014 Files to Reference (What to Fix)

```
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/domain/entities/ui_descriptor.py
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/application/dtos/requests.py
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/application/dtos/responses.py
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/frontend/types/widget-types.ts
```

### Target Structure (To Create)

```
/home/riju279/Documents/Code/XRIG/AgentX/agentx/ui/descriptors/base.py          # BaseUIDescriptor, UIDescriptorType
/home/riju279/Documents/Code/XRIG/AgentX/agentx/ui/protocols/websocket_messages.py  # All WebSocket types
/home/riju279/Documents/Code/XRIG/AgentX/agentx/application/dtos/ui_dtos.py        # Request/Response DTOs
/home/riju279/Documents/Code/XRIG/AgentX/frontend/types/descriptors.ts     # Zod schemas matching Pydantic
```

---

## 6. Critical Mismatches Found

### 6.1 Field Name Mismatches

| LLD (Correct) | R014 Backend (Wrong) | R014 Frontend |
|---------------|---------------------|----------------|
| `descriptor_id` | `id` | `descriptor_id` ✅ |
| `descriptor_type` | `type` | `descriptor_type` ✅ |
| `display_name` | (missing) | (missing) |

### 6.2 Type Value Mismatches

| LLD Enum | Value | R014 Value | Match? |
|----------|-------|------------|--------|
| `MARKDOWN_BLOCK` | `"markdown_block"` | `"markdown"` | ❌ |
| `CARD` | `"card"` | `"card"` | ✅ |
| `FORM` | `"form"` | `"form"` | ✅ |
| `PROGRESS` | `"progress"` | `"progress"` | ✅ |
| `ACTION` | `"action"` | `"action"` | ✅ |
| `CONFIRMATION` | `"confirmation"` | `"confirmation"` | ✅ |
| `VOICE` | `"voice"` | `"voice"` | ✅ |

### 6.3 Extra Types in R014 (Not in LLD)

| R014 Type | Should Be? | Action |
|-----------|------------|--------|
| `"image"` | Plugin only | Remove from core |
| `"gallery"` | Plugin only | Remove from core |
| `"chart"` | Plugin only | Remove from core |
| `"search-result"` | Composed type | Use MARKDOWN_BLOCK + citations |
| `"hop-progress"` | Composed type | Use PROGRESS + metadata |
| `"citation-card"` | Composed type | Use CARD + citations |

---

**Next Artifact**: extract.md
