# Specs Artifact: c001-folder-structure

**Generated**: 2026-01-28
**Change**: c001-folder-structure
**Schema**: spec-factory v1

---

## Spec Structure

This artifact generates domain-specific specification files in `specs/{domain}/spec.md`.

---

## 1. Spec: backend-folder-structure

**File**: `specs/backend-folder-structure/spec.md`

**Purpose**: Define the backend folder structure for Real AgentX v0.1, following Clean Architecture principles from mimicus with locked entities from LLD.

**Key Requirements**:
- 7-layer Clean Architecture: core/, domain/, infrastructure/, agent/, ui/, application/, presentation/
- Domain entities use @dataclass with business methods
- Repository interfaces are ABC in domain/repositories/
- All imports are absolute (no `from .` or `from ..`)
- No file exceeds 150 lines

**Acceptance Criteria**:
- [ ] All 7 directories exist with correct subdirectories
- [ ] All entities are @dataclass with business methods
- [ ] All repositories follow ABC pattern
- [ ] All imports are absolute paths
- [ ] No files exceed 150 lines

---

## 2. Spec: frontend-folder-structure

**File**: `specs/frontend-folder-structure/spec.md`

**Purpose**: Define the frontend folder structure for Real AgentX v0.1, following Next.js 15 App Router with atomic state pattern from R014.

**Key Requirements**:
- Next.js 15 App Router structure
- Components organized in components/ui/, components/descriptors/, components/layout/
- State uses Zustand with Immer
- Widget state uses atomic slice pattern
- No component exceeds 300 lines

**Acceptance Criteria**:
- [ ] All directories exist with correct structure
- [ ] Atomic state pattern implemented for widgets
- [ ] All components < 300 lines
- [ ] All TypeScript passes `npx tsc --noEmit`

---

## 3. Spec: file-naming-conventions

**File**: `specs/file-naming-conventions/spec.md`

**Purpose**: Define consistent file naming conventions to avoid the scattered model problems in R014.

**Key Requirements**:
- Domain entities in `domain/entities/<name>.py`
- Repository interfaces in `domain/repositories/<name>_repository.py`
- DTOs in `application/dtos/requests.py` or `application/dtos/responses.py`
- NEVER create `models.py` or `schemas.py` in service folders
- Entity/DTO/UseCase/Mapper suffixes used consistently

**Acceptance Criteria**:
- [ ] All files follow naming conventions
- [ ] Zero `models.py` files in service folders
- [ ] Zero `schemas.py` files in service folders
- [ ] All data models consolidated to domain/ or application/dtos/

---

## 4. Cross-Domain Contracts

### 4.1 Shared Types

| Type | Backend Location | Frontend Location |
|------|------------------|-------------------|
| Session state | domain/entities/enums.py (SessionState) | types/enums.ts (SessionState) |
| UI component types | domain/entities/enums.py (UIComponentType) | types/descriptors.ts (UIDescriptorType) |
| Widget descriptors | ui/descriptors/*.py | types/descriptors.ts |

### 4.2 Integration Points

| Backend Domain | Frontend Domain | Interface |
|----------------|-----------------|-----------|
| ui/descriptors/ | components/descriptors/ | Descriptor types |
| ui/protocols/websocket_messages.py | hooks/useWebSocket.ts | WebSocket protocol |
| application/dtos/ | types/api-*.ts | REST API contracts |

---

## 5. Spec: voice-client-structure (NEW from c010-voice-client)

**File**: `specs/voice-client-structure/spec.md`

**Purpose**: Define folder structure for voice client components (backend and frontend) for kyutai voice-server integration.

### Backend Voice Client Structure

```
agentx/
├── domain/
│   └── entities/
│       └── conversation_session.py          # ConversationSession, ConversationMessage, ConversationContext
├── application/
│   ├── dtos/
│   │   └── voice_gateway_dtos.py            # KyutaiMessage, KyutaiMessageType, DTOs
│   └── use_cases/
│       └── conversation_state_manager.py    # ConversationStateManager
└── infrastructure/
    └── external/
        ├── voice_gateway_service.py         # VoiceGatewayService (bridges frontend ↔ kyutai)
        ├── voice_protocol.py                 # Kyutai protocol helpers
        └── text_stream_handler.py            # TextStreamHandler (buffer, split, interrupt)
```

### Frontend Voice Client Structure

```
frontend/
├── lib/
│   └── voice/
│       ├── client.ts                        # VoiceClient (WebSocket connection)
│       ├── types.ts                         # TypeScript types for voice protocol
│       └── conversation.ts                  # Conversational state helpers
└── types/
    └── voice-protocol.ts                    # Zod schemas for voice protocol
```

**Key Requirements**:
- Backend voice components follow Clean Architecture (domain, application, infrastructure layers)
- Frontend voice components organized in lib/voice/ for client library
- All voice DTOs use Pydantic v2 with Field aliases (snake_case → camelCase)
- All voice types have corresponding Zod schemas in frontend
- No file exceeds 150 lines (CLAUDE_POLICY.md Rule 3)

**Acceptance Criteria**:
- [ ] domain/entities/conversation_session.py exists with ConversationSession entity
- [ ] application/dtos/voice_gateway_dtos.py exists with KyutaiMessage model
- [ ] application/use_cases/conversation_state_manager.py exists
- [ ] infrastructure/external/voice_gateway_service.py exists
- [ ] infrastructure/external/voice_protocol.py exists
- [ ] infrastructure/external/text_stream_handler.py exists
- [ ] lib/voice/client.ts exists with VoiceClient class
- [ ] lib/voice/types.ts exists with TypeScript types
- [ ] lib/voice/conversation.ts exists with conversation helpers
- [ ] types/voice-protocol.ts exists with Zod schemas
- [ ] All files pass ruff check, ruff format, pyrefly check (backend)
- [ ] All files pass ESLint check, TypeScript type check (frontend)

---

**Next Artifact**: design.md
