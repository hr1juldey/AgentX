
# Specs Artifact: c002-data-contracts

**Generated**: 2026-01-29 (Updated with LangGraph server-driven UI)
**Change**: c002-data-contracts
**Schema**: spec-factory v1

---

## 1. Spec: ui-descriptor-contracts

**File**: `specs/ui-descriptor-contracts/spec.md`

**Purpose**: Define UI descriptor contracts for LangGraph server-driven UI with Pydantic v2 ↔ Zod alignment and Shadow DOM isolation.

**Key Requirements**:
- Backend uses Pydantic v2 with Field aliases (snake_case → camelCase)
- Frontend uses Zod validation schemas matching Pydantic exactly
- 12 widget types from R014 + C007 exploration
- Components use Shadow DOM for style isolation
- Component registration in langgraph.json

**Widget Types**:
`markdown`, `card`, `form`, `progress`, `action`, `confirmation`, `image`, `gallery`, `chart`, `search-result`, `hop-progress`, `citation-card`

**Acceptance Criteria**:
- [ ] All 12 widget types defined in both backend and frontend
- [ ] Pydantic models use v2 syntax with Field aliases
- [ ] Zod schemas match Pydantic models exactly
- [ ] Components use Shadow DOM for style isolation
- [ ] Component registration in langgraph.json

---

## 2. Spec: pydantic-zod-sync

**File**: `specs/pydantic-zod-sync/spec.md`

**Purpose**: Establish single source of truth mapping Pydantic v2 to Zod with field alias handling and enum parity verification.

**Key Requirements**:
- Backend Pydantic is source of truth
- Frontend Zod schemas match field names exactly
- Field aliases map snake_case → camelCase
- Optional fields: `T | None` ↔ `TSchema.optional()`
- Enum values match exactly (case-sensitive)
- CI verification script for enum parity

**Type Mappings**:
| Python Type | Pydantic Field | TypeScript Type | Zod Schema |
|-------------|---------------|-----------------|------------|
| `str` | `Field()` | `string` | `z.string()` |
| `int` | `Field()` | `number` | `z.number()` |
| `list[T]` | `Field(default_factory=list)` | `T[]` | `z.array(TSchema)` |
| `T | None` | `Field(default=None)` | `T | undefined` | `TSchema.optional()` |
| `datetime` | `Field()` | `string` (ISO 8601) | `z.string().datetime()` |
| `Enum` | `enum.Enum` | `enum` | `z.enum([...])` |

**Acceptance Criteria**:
- [ ] All Pydantic models have corresponding Zod schemas
- [ ] Field aliases map snake_case → camelCase
- [ ] Enum values match exactly
- [ ] Optional fields consistent across both
- [ ] Nested objects recursively mapped
- [ ] CI verification script passes
- [ ] Type checking passes (tsc --noEmit, pyright)

---

## 3. Spec: websocket-protocol

**File**: `specs/websocket-protocol/spec.md`

**Purpose**: Define LangGraph server-driven UI protocol using `ui_message_reducer` for state management and `push_ui_message()` for backend emission.

**Key Requirements**:
- Frontend uses LangGraph SDK `useStream()` hook
- Frontend uses `onCustomEvent` callback for UI updates
- Frontend uses `ui_message_reducer` for state management
- Backend uses `push_ui_message()` to emit UI
- Backend nodes access `state.ui` for state awareness
- Streaming updates use `merge=True` with same message ID
- Components rendered via `LoadExternalComponent`
- Components colocated in agent/ui.tsx

**Message Structure** (AnyUIMessage):
```python
{
    "id": str,        # Unique message ID (uuid.uuid4())
    "name": str,      # Component name (matches ui.tsx export)
    "props": dict,    # Component props (match TypeScript interface)
    "metadata": dict, # Optional metadata
}
```

**Acceptance Criteria**:
- [ ] Frontend uses `useStream()` hook with `onCustomEvent`
- [ ] Frontend uses `ui_message_reducer` for state updates
- [ ] Backend nodes use `push_ui_message()` to emit UI
- [ ] Backend nodes access `state.ui` for state awareness
- [ ] Streaming updates use `merge=True` with same message ID
- [ ] Components rendered via `LoadExternalComponent`
- [ ] Components colocated in agent/ui.tsx
- [ ] Shadow DOM prevents style conflicts
- [ ] LangGraph server on port 2024

---

## 4. Cross-Domain Contracts

### 4.1 Shared Type Mappings

| Pydantic v2 | Zod | Location |
|-------------|-----|----------|
| `str` | `z.string()` | types/descriptors.ts |
| `str | None` | `z.string().optional()` | types/descriptors.ts |
| `int` | `z.number()` | types/descriptors.ts |
| `float` | `z.number()` | types/descriptors.ts |
| `bool` | `z.boolean()` | types/descriptors.ts |
| `datetime` | `z.string().datetime()` | types/descriptors.ts |
| `Dict[str, Any]` | `z.record(z.unknown())` | types/descriptors.ts |
| `list[T]` | `z.array(TSchema)` | types/descriptors.ts |
| `Enum` | `z.enum([...])` | types/descriptors.ts |

### 4.2 Field Alias Pattern

| Backend (Pydantic v2) | Frontend (Zod) |
|---------------------|----------------|
| `descriptor_id: str = Field(alias="id")` | `id: z.string()` |
| `descriptor_type: str = Field(alias="type")` | `type: z.string()` |
| `max_hops: int = Field(alias="maxHops")` | `maxHops: z.number()` |

### 4.3 Integration Points

| Backend Domain | Frontend Domain | Interface |
|----------------|-----------------|-----------|
| `agentx/ui/descriptors/*.py` | `frontend/types/descriptors.ts` | UI descriptor types |
| `agentx/agent/ui.tsx` | `frontend/app/` | LangGraph server-driven UI |
| `langgraph.graph.ui.push_ui_message()` | `@langchain/langgraph-sdk/react` | UI emission protocol |
| `application/dtos/*.py` | `frontend/types/api-*.ts` | REST API contracts |

### 4.4 Component Registration Mapping

| Component Name | Backend Emission | Frontend Export | Location |
|----------------|-----------------|-----------------|----------|
| markdown | `push_ui_message("markdown", {...})` | `markdown: MarkdownComponent` | agent/ui.tsx |
| card | `push_ui_message("card", {...})` | `card: CardComponent` | agent/ui.tsx |
| form | `push_ui_message("form", {...})` | `form: FormComponent` | agent/ui.tsx |
| progress | `push_ui_message("progress", {...})` | `progress: ProgressComponent` | agent/ui.tsx |
| action | `push_ui_message("action", {...})` | `action: ActionComponent` | agent/ui.tsx |
| confirmation | `push_ui_message("confirmation", {...})` | `confirmation: ConfirmationComponent` | agent/ui.tsx |
| image | `push_ui_message("image", {...})` | `image: ImageComponent` | agent/ui.tsx |
| gallery | `push_ui_message("gallery", {...})` | `gallery: GalleryComponent` | agent/ui.tsx |
| chart | `push_ui_message("chart", {...})` | `chart: ChartComponent` | agent/ui.tsx |
| searchResult | `push_ui_message("search-result", {...})` | `searchResult: SearchResultComponent` | agent/ui.tsx |
| hopProgress | `push_ui_message("hop-progress", {...})` | `hopProgress: HopProgressComponent` | agent/ui.tsx |
| citationCard | `push_ui_message("citation-card", {...})` | `citationCard: CitationCardComponent` | agent/ui.tsx |
| voiceStatus | `push_ui_message("voiceStatus", {...})` | `voiceStatus: VoiceNucleusWidget` | agent/ui.tsx |

---

## 5. Architectural Changes from R014

### 5.1 R014 Pattern (Deprecated)

- **WebSocket descriptor-only**: Backend sent data only, frontend rendered
- **Nested callbacks**: `widget_callback=send_widget`, `qa_callback=send_qa_progress`
- **No state awareness**: Designer agent couldn't see existing widgets
- **Global CSS**: Style conflicts between widgets

### 5.2 LangGraph Pattern (New)

- **Server-driven UI**: Backend sends code + data via LoadExternalComponent
- **State-based**: `ui_message_reducer` tracks all UI state in `state.ui`
- **Designer agent fix**: Can access `state.ui` to avoid repeating widgets
- **Shadow DOM**: Guaranteed style isolation

---

## 6. Spec: voice-protocol-contracts (NEW from c010-voice-client)

**File**: `specs/voice-protocol-contracts/spec.md`

**Purpose**: Define voice streaming data contracts for kyutai voice-server integration with Pydantic v2 ↔ Zod alignment.

**Key Requirements**:
- Backend uses Pydantic v2 with Field aliases for kyutai protocol
- Frontend uses Zod validation schemas matching Pydantic exactly
- Kyutai message types: Config, Audio, Text, Error, Eos, Heartbeat
- Conversational state models: ConversationSession, ConversationMessage, ConversationContext
- MessageRole enum: USER, ASSISTANT, SYSTEM

**Kyutai Protocol Types**:
`KyutaiMessageType` (CONFIG, AUDIO, TEXT, ERROR, EOS, HEARTBEAT)

**Conversational State Types**:
`MessageRole` (USER, ASSISTANT, SYSTEM)
`ConversationSession` (session tracking)
`ConversationMessage` (message with role, content, timestamp)
`ConversationContext` (topic, entities, sentiment, language, timezone)

**Acceptance Criteria**:
- [ ] KyutaiMessage Pydantic model validates kyutai protocol
- [ ] KyutaiMessage Zod schema matches Pydantic model
- [ ] ConversationSession Pydantic model tracks session state
- [ ] ConversationSession Zod schema matches Pydantic model
- [ ] MessageRole enum values match exactly (Pydantic ↔ Zod)
- [ ] Field aliases map snake_case → camelCase (sessionId, messageId, etc.)
- [ ] Optional fields use .optional() in Zod, default=None in Pydantic

**Integration Points** (NEW):

| Backend Domain | Frontend Domain | Interface |
|----------------|-----------------|-----------|
| `agentx/application/dtos/voice_gateway_dtos.py` | `frontend/types/voice-protocol.ts` | Kyutai protocol types |
| `agentx/domain/entities/conversation_session.py` | `frontend/types/voice-protocol.ts` | Conversational state types |
| `infrastructure/external/voice_gateway_service.py` | `lib/voice/client.ts` | Voice gateway client |

**Component Registration Mapping** (NEW):

| Message Type | Backend Emission | Frontend Handler | Location |
|--------------|-----------------|------------------|----------|
| Config (kyutai) | `KyutaiMessage(type=CONFIG)` | VoiceClient sends config | lib/voice/client.ts |
| Audio (kyutai) | `KyutaiMessage(type=AUDIO)` | VoiceGatewayService routes | voice_gateway_service.py |
| Text (kyutai) | `KyutaiMessage(type=TEXT)` | Transcript / TTS input | voice_gateway_service.py |
| Error (kyutai) | `KyutaiMessage(type=ERROR)` | Error display | VoiceClient handler |
| Eos (kyutai) | `KyutaiMessage(type=EOS)` | Buffer flush | voice_stream_handler.py |
| Heartbeat (kyutai) | `KyutaiMessage(type=HEARTBEAT)` | Connection keep-alive | VoiceGatewayService |

---

**Next Artifact**: design.md
