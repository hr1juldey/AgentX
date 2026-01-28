# Design Artifact: c002-data-contracts

**Generated**: 2026-01-28
**Change**: c002-data-contracts
**Schema**: spec-factory v1

---

## 1. Architecture

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                  Data Contract Flow                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  LLD (Source of Truth)                                         │
│  ┌─────────────────────────────────────────────┐                │
│  │ ui_descriptor_contract.md (Locked)        │                │
│  └──────────────────┬──────────────────────────┘                │
│                     │                                           │
│                     ▼                                           │
│  Backend (Pydantic v2)                                          │
│  ┌─────────────────────────────────────────────┐                │
│  │ agentx/ui/descriptors/base.py              │                │
│  │ agentx/ui/descriptors/*.py (7 types)       │                │
│  │ agentx/ui/protocols/websocket_messages.py  │                │
│  │ agentx/application/dtos/*.py               │                │
│  └──────────────────┬──────────────────────────┘                │
│                     │ WebSocket / HTTP                        │
│                     ▼                                           │
│  Frontend (Zod)                                                │
│  ┌─────────────────────────────────────────────┐                │
│  │ frontend/types/descriptors.ts             │                │
│  │ frontend/types/websocket.ts              │                │
│  │ frontend/types/api-*.ts                   │                │
│  └─────────────────────────────────────────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 File Structure

```
agentx/
├── ui/
│   ├── descriptors/
│   │   ├── base.py              # BaseUIDescriptor, UIDescriptorType
│   │   ├── markdown_block.py    # MarkdownBlockDescriptor
│   │   ├── card.py              # CardDescriptor, CardAction
│   │   ├── form.py              # FormDescriptor, FormField, FormFieldType
│   │   ├── progress.py          # ProgressDescriptor
│   │   ├── action.py            # ActionDescriptor
│   │   ├── confirmation.py     # ConfirmationDescriptor
│   │   └── voice.py             # VoiceDescriptor
│   └── protocols/
│       └── websocket_messages.py # WebSocketMessage, all payloads
│
└── application/
    └── dtos/
        ├── requests.py           # GenerateWidgetRequestDTO, SearchRequestDTO
        ├── responses.py          # SearchResultResponseDTO, WidgetResponseDTO
        └── ui_dtos.py             # UIDescriptorResponseDTO

frontend/
└── types/
    ├── descriptors.ts            # Zod schemas matching Pydantic
    ├── websocket.ts             # WebSocket message schemas
    └── api-requests.ts          # API request Zod schemas
```

---

## 2. Data Flow

### 2.1 Contract Generation Flow

```
LLD (Locked)
  │
  ├─→ Backend Pydantic (Implementation)
  │     ↓
  │   WebSocket/HTTP
  │     ↓
  └─→ Frontend Zod (Implementation)
       (Must match Pydantic exactly)
```

### 2.2 Type Validation Flow

```
Client Request
  ↓
Zod Schema Validation (Frontend)
  ↓
API Request (validated)
  ↓
Pydantic Validation (Backend)
  ↓
Business Logic
  ↓
Pydantic Response (validated)
  ↓
WebSocket/HTTP Response
  ↓
Zod Schema Validation (Frontend)
  ↓
UI Render
```

---

## 3. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| Pydantic version | v2 (`str \| None`) | v1 (`Optional[str]`) | v2 is modern, cleaner syntax |
| Frontend validation | Zod | TypeScript interfaces, io-ts | Zod provides runtime validation |
| Source of truth | LLD documents | R014 code | LLD is locked, R014 has bugs |
| Field naming | LLD names (`descriptor_id`) | R014 names (`id`) | LLD is authoritative |
| Type values | LLD enum values (`markdown_block`) | R014 values (`markdown`) | LLD is authoritative |

---

## 4. Tradeoff Analysis

### 4.1 Approach A: Fix Backend to Match LLD

| Aspect | Rating | Notes |
|--------|--------|-------|
| Correctness | ⭐⭐⭐ | Matches LLD exactly |
| Effort | ⭐⭐ | Requires changing R014 backend |
| Breaking | ⭐⭐ | Breaks R014 frontend (but it's prototype) |

**Pros**:
- Single source of truth
- Type safety across stack
- Clear contract definitions

**Cons**:
- Breaking change to R014
- Requires updates to both backend and frontend

### 4.2 Approach B: Match R014 (Do Nothing)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Correctness | ⭐ | Violates LLD |
| Effort | ⭐⭐⭐ | No changes needed |
| Breaking | ⭐⭐⭐ | No breaking changes |

**Pros**:
- No changes to existing code

**Cons**:
- Perpetuates LLD violations
- Field name confusion (`id` vs `descriptor_id`)
- Type value drift (`markdown` vs `markdown_block`)

### 4.3 Decision: Fix Backend to Match LLD (Approach A)

**Rationale**: LLD is the source of truth. R014 is a prototype with known issues. Fixing contracts now prevents long-term drift.

---

## 5. Implementation Details

### 5.1 Key Files to Create

| File | Purpose | Lines (est.) |
|------|---------|--------------|
| `agentx/ui/descriptors/base.py` | BaseUIDescriptor, UIDescriptorType | 70 |
| `agentx/ui/descriptors/markdown_block.py` | MarkdownBlockDescriptor | 40 |
| `agentx/ui/descriptors/card.py` | CardDescriptor, CardAction | 60 |
| `agentx/ui/descriptors/form.py` | FormDescriptor, FormField, FormFieldType | 120 |
| `agentx/ui/protocols/websocket_messages.py` | All WebSocket types | 200 |
| `frontend/types/descriptors.ts` | Zod schemas matching Pydantic | 250 |

### 5.2 Type Mapping Examples

**Pydantic v2**:
```python
class BaseUIDescriptor(BaseModel):
    descriptor_id: str
    descriptor_type: UIDescriptorType
    display_name: Optional[str]
    metadata: Dict[str, Any]
```

**Zod**:
```typescript
const BaseUIDescriptorSchema = z.object({
  descriptor_id: z.string(),
  descriptor_type: z.enum(["markdown_block", "card", ...]),
  display_name: z.string().optional(),
  metadata: z.record(z.any()),
});
```

---

## 6. Security Considerations

| Concern | Mitigation |
|---------|------------|
| Type injection | Zod runtime validation on all inputs |
| Enum overflow | Closed set in both Pydantic Literal and Zod enum |
| Field name confusion | Consistent naming across stack |

---

## 7. Performance Considerations

| Concern | Mitigation |
|---------|------------|
| Validation overhead | Minimal with Pydantic/Zod (both compiled) |
| Schema duplication | Acceptable tradeoff for type safety |

---

**Next Artifact**: tasks.md
