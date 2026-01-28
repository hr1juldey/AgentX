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
├── agent/                             # Layer 3: DSPy Agents & LangGraph
│   ├── __init__.py                    # Package init
│   ├── graph.py                       # LangGraph StateGraph definition
│   ├── state.py                       # AgentState TypedDict with ui_message_reducer
│   ├── ui.tsx                         # React components (colocated!)
│   │                                  # └── Export default {component, ...}
│   ├── nodes/                         # LangGraph nodes
│   │   ├── analyst.py                 # Query understanding
│   │   ├── designer.py                # UI widget selection (state aware!)
│   │   └── ...
│   ├── dspy_signatures/               # DSPy signatures
│   ├── tools/                         # DSPy tools
│   └── dspy_agents/                   # ReAct agents
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
├── langgraph.json                     # Graph + UI component mapping
├── core/middleware/                   # Hardening (Phase 7)
├── monitoring/                        # Metrics, health checks (Phase 7)
└── tests/                             # Tests (Phase 7)
```

### 1.2.1 LangGraph Component Colocation Pattern

**Decision**: Use LangGraph server-driven UI with component colocation.

**Structure**:
```
agent/
├── graph.py              # StateGraph with ui_message_reducer
├── state.py              # AgentState TypedDict
├── ui.tsx                # React components (colocated!)
└── nodes/
    ├── designer.py       # UI widget selection with state awareness
    └── ...
```

**ui.tsx export pattern**:
```typescript
export default {
  markdown: MarkdownComponent,
  card: CardComponent,
  form: FormComponent,
  progress: ProgressComponent,
  // ... 12 widget types total
};
```

**langgraph.json mapping**:
```json
{
  "graphs": {
    "agent": "./agent/graph.py"
  },
  "ui": {
    "agent": "./agent/ui.tsx"
  }
}
```

**Rationale** (from C007 exploration):
- Components bundled and served by LangSmith
- Backend has full control (code + data)
- Designer agent gets state awareness via `state.ui`
- Shadow DOM for style isolation
- Industry standard (LangSmith/LangChain)

### 1.3 Frontend Structure

```
/home/riju279/Documents/Code/XRIG/AgentX/frontend/
├── app/                               # Next.js App Router
│   ├── layout.tsx                     # Root layout
│   ├── page.tsx                       # Home page with useStream hook
│   └── globals.css                    # Tailwind + shadcn/ui
│
├── components/                        # React components
│   ├── metaball-canvas.tsx            # SVG metaball filter (C008)
│   ├── voice-button.tsx               # Central nucleus for voice (C008)
│   ├── ui/                            # shadcn/ui base components
│   └── layout/                        # Layout components
│
├── design/                            # Organic UI Design Layer (C008)
│   ├── tokens.ts                      # Design tokens (colors, spacing, timing)
│   ├── motion.ts                      # Motion presets (mitosis, pulse, drift)
│   └── surfaces.tsx                   # Primitives (Cell, Nucleus)
│
├── hooks/                             # Custom React hooks
│   └── useWebSocket.ts                # WebSocket connection
│
├── types/                             # TypeScript types
│   ├── descriptors.ts                 # UI descriptor types
│   ├── websocket.ts                   # WebSocket message types
│   └── api.ts                         # API response types
│
├── langgraph-sdk/                     # LangGraph SDK integration
│   └── useStream.ts                   # Wrapper for @langchain/langgraph-sdk/react
│
├── tailwind.config.ts
├── next.config.js
└── tsconfig.json
```

### 1.3.1 LangGraph Frontend Integration

**page.tsx pattern** (from C007 exploration):
```tsx
import { useStream } from "@langchain/langgraph-sdk/react";
import { LoadExternalComponent } from "@langchain/langgraph-sdk/react-ui";

const { thread, values } = useStream({
  apiUrl: "http://localhost:2024",
  assistantId: "agent",
  onCustomEvent: (event, options) => {
    options.mutate((prev) => {
      const ui = uiMessageReducer(prev.ui ?? [], event);
      return { ...prev, ui };
    });
  },
});

return (
  <>
    {values.ui?.map((ui) => (
      <LoadExternalComponent
        key={ui.id}
        stream={thread}
        message={ui}
        fallback={<SkeletonWidget />}
      />
    ))}
  </>
);
```

### 1.3.2 Organic UI Design Layer (C008)

**Design tokens** (from agentx_organic_ui_design_system.md):
```typescript
// design/tokens.ts
export const tokens = {
  color: {
    void: '#0A0A0A',        // Deep space background
    membrane: '#141414',     // Primary surface
    enzyme: '#00D9FF',       // Cyan accent
  },
  metaball: {
    desktopBlur: 16,
    mobileBlur: 12,
    mobileMaxBlobs: 6,
    desktopMaxBlobs: 12,
    radius: {
      voice: 160,           // Desktop nucleus
      voiceMobile: 72,       // Mobile nucleus
    }
  }
};
```

**Motion presets**:
```typescript
// design/motion.ts
export const motion = {
  mitosis: { duration: 0.8, ease: [0.16, 1, 0.3, 1] },
  pulse: { duration: 2, repeat: Infinity },
  drift: { duration: 20, repeat: Infinity },
};
```

**Rationale** (from C007 exploration):
- Organic UI as visual skin layer (not widget delivery)
- LangGraph server-driven UI handles widget delivery
- 2D metaballs (not 3D) for performance
- Platform-aware: 16px blur desktop, 12px mobile

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

### 2.2 LangGraph Server-Driven UI Flow

```
Frontend (useStream hook)
      ↓
onCustomEvent callback
      ↓
uiMessageReducer (state update)
      ↓
LoadExternalComponent (fetches and renders)
      ↓
LangSmith Bundle Server
      ↓
Backend ui.tsx (colocated components)
```

**Backend emission pattern** (from C007 exploration):
```python
from langgraph.graph.ui import push_ui_message, ui_message_reducer

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]

async def designer_node(state: AgentState):
    existing_widgets = [msg.name for msg in state.ui]  # State awareness!
    push_ui_message("card", {"title": "..."}, message=message)
    return {"messages": [message]}
```

**Streaming with merge pattern**:
```python
ui_message = push_ui_message("writer", {"title": "..."}, message=message)
ui_message_id = ui_message["id"]

for chunk in content_stream:
    push_ui_message(
        "writer",
        {"content": chunk.text},
        id=ui_message_id,  # Same ID!
        merge=True,        # Merge props!
        message=message,
    )
```

### 2.3 Port Assignments

| Service | Port | Purpose | Source |
|---------|------|---------|--------|
| **LangGraph Server** | 2024 | Main agent server (LangGraph default) | C007 exploration |
| **Frontend Dev** | 3000 | Next.js dev server | Next.js default |
| **Voice API** | 8015 | Audio streaming | C004 |
| **Search API** | 8016 | Web search service | C005 |

**Note**: LangGraph default port is 2024, avoids 8000-8014 range per constraints.

---

## 3. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| Layer count | 7 layers | 5 layers (mimicus), 6 layers | AgentX needs `agent/` and `ui/` layers for DSPy and UI descriptors |
| `agent/` layer | Separate from domain/ | Merge into domain/ | DSPy agents don't fit domain (has external deps: LM, tools) |
| `ui/` layer | Separate from domain/ | Merge into domain/ | UI descriptors need WebSocket protocols (infrastructure concern) |
| **UI architecture** | **LangGraph server-driven** | R014 descriptor-only, React-only | **Backend has full control, state awareness, Shadow DOM isolation (C007)** |
| **Component placement** | **Colocated with graph** | Separate frontend repo | **Industry standard (LangSmith), single source of truth (C007)** |
| **State management** | **ui_message_reducer** | Zustand atomic slices | **Automatic state tracking, Designer agent awareness (C007)** |
| **Style isolation** | **Shadow DOM** | Global CSS, CSS-in-JS | **Guaranteed isolation, no style conflicts (C007)** |
| Import style | Absolute only | Relative imports | CLAUDE_POLICY.md requirement, proven by R014 |
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
