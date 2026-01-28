# Design Artifact: c007-frontend-architecture

**Generated**: 2026-01-29
**Change**: c007-frontend-architecture
**Schema**: spec-factory v1.0.0

---

## 1. Architecture

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LangGraph Server-Driven UI Architecture                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Backend (Python)                              │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  LangGraph State (AgentState)                               │  │   │
│  │  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │  │   │
│  │  │  │  messages   │  │      ui      │  │   ui_message_   │  │  │   │
│  │  │  │ (add_msgs)  │  │ (Sequence)   │  │    reducer      │  │  │   │
│  │  │  └─────────────┘  │ (AnyUIMsg)   │  │ (auto tracking) │  │  │   │
│  │  │                  └──────────────┘  └──────────────────┘  │  │   │
│  │  │                           │                              │  │  │   │
│  │  │                           ▼                              │  │  │   │
│  │  │                  ┌─────────────────────┐                   │  │  │   │
│  │  │                  │  push_ui_message()  │                   │  │  │   │
│  │  │                  │  ("card", {...})     │                   │  │  │   │
│  │  │                  └─────────────────────┘                   │  │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Frontend (Next.js)                           │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  useStream() Hook                                           │  │   │
│  │  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │  │   │
│  │  │  │  thread     │  │    values    │  │   onCustomEvent│  │  │   │
│  │  │  │             │  │              │  │                  │  │  │   │
│  │  │  └─────────────┘  └──────────────┘  │   ui_msg_reducer │  │  │   │
│  │  │                                        │                  │  │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │  LoadExternalComponent (Shadow DOM Isolated)              │  │   │
│  │  │  ┌──────────────────────────────────────────────────────┐   │  │   │
│  │  │  │  Widget Component (from ui.tsx registry)            │   │  │   │
│  │  │  │  ┌─────────────┐  ┌──────────────┐                     │   │  │   │
│  │  │  │  │    props    │  │   Shadow DOM │                     │   │  │   │
│  │  │  │  └─────────────┘  └──────────────┘                     │   │  │   │
│  │  │  └──────────────────────────────────────────────────────┘   │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Layer Structure (Frontend)

```
frontend/
├── src/
│   ├── agent/              # LangGraph integration (colocated)
│   │   ├── graph.ts        # LangGraph state definition
│   │   └── ui.tsx         # Widget registry (default export)
│   ├── components/
│   │   └── ui/            # Widget components
│   │       ├── widgets/    # 12 widget types
│   │       │   ├── MarkdownWidget.tsx
│   │       │   ├── CardWidget.tsx
│   │       │   └── ...
│   │       └── voice-nucleus/
│   └── pages/             # Next.js pages
└── package.json            # Dependencies
```

---

## 2. Data Flow

### 2.1 Widget Rendering Flow

```
1. Backend emits widget:
   Python Backend (C003)
      │
      │  push_ui_message(
      │    "card",
      │    {"title": "...", "content": "..."},
      │    message=message
      │  )
      │
      ▼
   LangGraph State (ui_message_reducer)
      │
      │  ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]
      │
      ▼
2. Frontend receives widget:
   Frontend (C007)
      │
      │  WebSocket / HTTP Stream
      │
      ▼
   useStream() Hook
      │
      │  onCustomEvent: (event, options) => {
      │    options.mutate((prev) => {
      │      const ui = uiMessageReducer(prev.ui ?? [], event)
      │      return { ...prev, ui }
      │    })
      │  }
      │
      ▼
3. Widget renders:
   LoadExternalComponent
      │
      │  Resolves component from ui.tsx registry
      │
      ▼
   Widget Component (Shadow DOM Isolated)
      │
      │  Renders with props from AnyUIMessage
      │
      ▼
   UI Display
```

---

## 3. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| **Server-driven UI** | Backend emits React components | Descriptor-only WebSocket | Full control, state awareness |
| **Component Colocation** | ui.tsx next to graph.py | Separate UI directory | Industry standard, easier maintenance |
| **Shadow DOM** | Style isolation per widget | CSS modules | Prevents all CSS conflicts |
| **ui_message_reducer** | Automatic state tracking | Manual state management | Simpler, less error-prone |
| **LangGraph SDK** | Industry-standard library | Custom WebSocket | Production-ready, documented |

---

## 4. Implementation Details

### 4.1 Key Classes/Modules

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| **src/agent/graph.ts** | LangGraph state definition | LangGraph SDK |
| **src/agent/ui.tsx** | Widget registry (12 components) | All widget components |
| **useStream()** | LangGraph streaming hook | @langchain/langgraph-sdk-react-ui |
| **LoadExternalComponent** | Render widget with Shadow DOM | @langchain/langgraph-sdk-react-ui |

### 4.2 Port Assignments

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| **Frontend (Next.js)** | 3000 | HTTP | Main frontend application |
| **LangGraph Server** | 2024 | HTTP | Backend graph execution (from C003) |

### 4.3 File Structure (Implementation)

```
frontend/src/
├── agent/
│   ├── graph.ts          # ~100 lines (LangGraph state)
│   └── ui.tsx            # ~50 lines (Widget registry)
├── components/ui/
│   └── widgets/          # 12 widget types (~80 lines each)
│       ├── MarkdownWidget.tsx
│       ├── CardWidget.tsx
│       └── ...
└── pages/               # Next.js pages
```

---

## 5. Security Considerations

| Concern | Mitigation |
|---------|------------|
| **XSS in Widget Props** | LangGraph server-driven UI ensures props are backend-generated |
| **Component Hijacking** | Shadow DOM isolation prevents component tampering |
| **WebSocket Security** | Use WSS (secure WebSocket) in production |

---

## 6. Performance Considerations

| Concern | Mitigation |
|---------|------------|
| **Bundle Size** | Tree-shake unused imports, monitor bundle size |
| **Shadow DOM Overhead** | Minimal overhead in modern browsers |
| **Widget Rendering** | Lazy loading, code splitting per widget |

---

**Next Artifact**: tasks.md
