# Design Artifact: c001-folder-structure

**Generated**: 2026-01-28
**Change**: c001-folder-structure
**Schema**: spec-factory v1

---

## 1. Architecture

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Real AgentX v0.1                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐         ┌─────────────────────────────────┐   │
│  │   Frontend      │         │   Backend (agentx/)             │   │
│  │   (Next.js 15)  │◀────────┤                                 │   │
│  │                 │ WebSocket│ ┌──────┐  ┌───────┐  ┌──────┐ │   │
│  │  components/    │         │ │ Fast │  │ Domain│  │ Infra │ │   │
│  │  store/         │ HTTP     │ │ API  │──│  /   │──│  /   │ │   │
│  │  types/         │◀────────┤ └──────┘  └───────┘  └──────┘ │   │
│  │  hooks/         │         │                                 │   │
│  └─────────────────┘         └─────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Backend Layer Structure (Clean Architecture)

```
/home/riju279/Documents/Code/XRIG/AgentX/agentx/
├── core/                              # Layer 0: Configuration & DI
│   ├── config.py                      # Pydantic Settings
│   ├── dependencies.py                # DI singletons
│   └── middleware/                    # CORS, logging, auth
│
├── domain/                            # Layer 1: Business Logic (Innermost)
│   ├── entities/                      # @dataclass entities
│   ├── value_objects/                 # Immutable value objects
│   ├── repositories/                  # ABC interfaces + implementations
│   └── services/                      # Domain services
│
├── infrastructure/                    # Layer 2: External Adapters
│   ├── database/                      # Redis, SQLite adapters
│   └── external/                      # Qdrant, Ollama, Mem0, WebSocket
│
├── agent/                             # Layer 3: DSPy Agents & Tools
│   ├── dspy_signatures/               # DSPy signatures
│   ├── tools/                         # DSPy tools
│   ├── dspy_agents/                   # ReAct agents
│   └── langgraph/                     # State machines
│
├── ui/                                # Layer 4: UI Descriptors
│   ├── descriptors/                    # UI descriptor classes
│   └── protocols/                     # WebSocket message schemas
│
├── application/                       # Layer 5: Use Cases & DTOs
│   ├── use_cases/                     # Single-purpose classes
│   ├── commands/                      # Command DTOs
│   ├── queries/                       # Query DTOs
│   ├── dtos/                          # Pydantic models (requests, responses)
│   ├── mappers/                       # Entity ↔ DTO conversion
│   └── services/                      # Application services
│
├── plugin/                            # Layer 6: Plugin System
│   ├── interface.py                   # AgentXPlugin ABC
│   ├── permissions.py                 # Plugin permissions
│   ├── manifest.py                    # Plugin manifests
│   └── registry.py                    # Plugin registry
│
├── presentation/                      # Layer 7: API Routes (Outermost)
│   └── api/v1/                        # REST endpoints
│       ├── agent_routes.py
│       └── plugin_routes.py
│
├── core/middleware/                   # Hardening (Phase 7)
├── monitoring/                        # Metrics, health checks (Phase 7)
└── tests/                             # Tests (Phase 7)
```

### 1.3 Frontend Structure

```
/home/riju279/Documents/Code/XRIG/AgentX/frontend/
├── app/                               # Next.js App Router
│   ├── layout.tsx                     # Root layout
│   ├── page.tsx                       # Home page
│   └── globals.css                    # Tailwind + shadcn/ui
│
├── components/                        # React components
│   ├── ui/                            # shadcn/ui base components
│   ├── descriptors/                   # UI descriptor renderers
│   └── layout/                        # Layout components
│
├── store/                             # Zustand stores
│   ├── network-store.ts               # WebSocket, API health
│   ├── ui-store.ts                    # UI state management
│   └── widget-store.ts                # Atomic widget state
│
├── types/                             # TypeScript types
│   ├── descriptors.ts                 # UI descriptor types
│   ├── websocket.ts                   # WebSocket message types
│   └── api.ts                         # API response types
│
├── hooks/                             # Custom React hooks
│   └── useWebSocket.ts                # WebSocket connection
│
├── tailwind.config.ts
├── next.config.js
└── tsconfig.json
```

---

## 2. Data Flow

### 2.1 Backend Request Flow

```
Client Request
      ↓
FastAPI Route (presentation/api/v1/)
      ↓
Use Case (application/use_cases/)
      ↓
    ├─→ DTO (application/dtos/)
    ├─→ Mapper (application/mappers/)
    └─→ Repository (infrastructure/)
            ↓
      Entity (domain/entities/)
```

### 2.2 WebSocket Widget Streaming Flow

```
Frontend Widget Store
      ↓
WebSocket Message (ui/protocols/websocket_messages.py)
      ↓
DSPy Agent (agent/dspy_agents/)
      ↓
UI Descriptor (ui/descriptors/)
      ↓
WebSocket Manager (infrastructure/external/websocket_manager.py)
      ↓
Frontend Component (components/descriptors/)
```

---

## 3. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| Layer count | 7 layers | 5 layers (mimicus), 6 layers | AgentX needs `agent/` and `ui/` layers for DSPy and UI descriptors |
| `agent/` layer | Separate from domain/ | Merge into domain/ | DSPy agents don't fit domain (has external deps: LM, tools) |
| `ui/` layer | Separate from domain/ | Merge into domain/ | UI descriptors need WebSocket protocols (infrastructure concern) |
| Import style | Absolute only | Relative imports | CLAUDE_POLICY.md requirement, proven by R014 |
| State pattern | Atomic slices | Record<string, Widget> | Proven by R014 to prevent cascade re-renders |
| File size limit | 150 lines | 100 lines (CLAUDE_POLICY.md) | Balance between clarity and modularity |

---

## 4. Tradeoff Analysis

### 4.1 Approach A: 5 Layers (Mimicus)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐⭐ | Fewer layers, easier to understand |
| Fit for AgentX | ⭐⭐ | DSPy agents don't fit cleanly |
| Proven | ⭐⭐⭐ | Works well for mimicus |

**Pros**:
- Fewer directories to navigate
- Established pattern from mimicus
- Simpler dependency graph

**Cons**:
- DSPy agents would have to go in domain/ (wrong - has external deps)
- UI descriptors would be in application/ (wrong - needs persistence)

### 4.2 Approach B: 7 Layers (Chosen)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐ | More layers, more complex |
| Fit for AgentX | ⭐⭐⭐ | Each concern has clear home |
| Proven | ⭐⭐ | New pattern, extends mimicus |

**Pros**:
- DSPy agents have their own layer (agent/)
- UI descriptors have their own layer (ui/)
- Clear separation: domain = pure business, agent = AI logic, ui = UI contracts

**Cons**:
- More directories to navigate
- Steeper learning curve for new developers
- More README.md files needed

### 4.3 Decision: 7 Layers

**Rationale**: AgentX has unique concerns (DSPy agents, UI descriptors) that don't fit mimicus's 5-layer model. The extra layers prevent forcing concepts where they don't belong.

---

## 5. Implementation Details

### 5.1 Key Files to Create

| Phase | File | Purpose | Lines (est.) |
|-------|------|---------|--------------|
| 0 | `agentx/core/config.py` | Pydantic Settings | 50 |
| 0 | `agentx/core/dependencies.py` | DI singletons | 30 |
| 0 | `agentx/main.py` | FastAPI entry point | 20 |
| 1 | `agentx/domain/entities/agent_session.py` | AgentSessionEntity | 70 |
| 1 | `agentx/domain/entities/ui_component.py` | UIComponentEntity | 60 |
| 1 | `agentx/domain/repositories/agent_session_repository.py` | ABC + implementations | 40 |
| 2 | `agentx/agent/dspy_signatures/main_signatures.py` | MainAgentSignature | 50 |
| 3 | `agentx/ui/descriptors/base.py` | BaseUIDescriptor | 40 |
| 4 | `agentx/agent/langgraph/backend_state_machine.py` | State machine | 150 |
| 7 | `agentx/core/middleware/error_handler.py` | Global error handling | 80 |

### 5.2 Port Assignments

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| AgentX API | 8015 | HTTP | Main API (C004) |
| WebSocket | 8016 | WS | Widget streaming (C003) |
| Voice STT | 8017 | HTTP | STT service (C004) |
| Voice TTS | 8018 | HTTP | TTS service (C004) |

### 5.3 Directory Creation Order

```bash
# Phase 0: Foundation
mkdir -p agentx/core/middleware
touch agentx/core/__init__.py agentx/core/config.py agentx/core/dependencies.py

# Phase 1: Domain + Infrastructure
mkdir -p agentx/domain/entities agentx/domain/value_objects agentx/domain/repositories agentx/domain/services
mkdir -p agentx/infrastructure/database agentx/infrastructure/external

# Phase 2: Agent layer
mkdir -p agentx/agent/dspy_signatures agentx/agent/tools agentx/agent/dspy_agents

# Phase 3: UI layer
mkdir -p agentx/ui/descriptors agentx/ui/protocols

# Phase 4: Application layer
mkdir -p agentx/application/use_cases agentx/application/commands agentx/application/queries
mkdir -p agentx/application/dtos agentx/application/mappers agentx/application/services

# Phase 5: Presentation layer
mkdir -p agentx/presentation/api/v1

# Phase 6: Plugin layer
mkdir -p agentx/plugin

# Phase 7: Hardening
mkdir -p agentx/core/middleware agentx/monitoring agentx/tests
```

---

## 6. Security Considerations

| Concern | Mitigation |
|---------|------------|
| Import confusion | Absolute imports only, enforced via ruff |
| File size violations | CI check: `find agentx/ -name "*.py" -exec wc -l {} + | awk '$1 > 150'` |
| Layer violations | Code review: check imports don't skip layers |
| Relative imports | Pre-commit hook: `grep -r "from \.\." agentx/` |

---

## 7. Performance Considerations

| Concern | Mitigation |
|---------|------------|
| Import overhead | Absolute imports may be slower, but negligible impact |
| File navigation | Use IDE jump-to-definition, layer README.md files |
| Module loading | Lazy loading via `get_<dependency>()` functions |

---

**Next Artifact**: tasks.md
