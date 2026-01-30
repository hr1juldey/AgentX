# Design Artifact: c008-organic-ui

**Generated**: 2026-01-29
**Change**: c008-organic-ui
**Schema**: spec-factory v1.0.0

---

## 1. Architecture

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Organic UI Architecture                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LangGraph Server-Driven UI (C007)                 │   │
│  │  ┌─────────────────┐        push_ui_message()       ┌──────────────┐ │   │
│  │  │  Backend Graph  │────────────────────────────────▶│   Frontend   │ │   │
│  │  │   (Python)      │    widget instructions         │  (Next.js)   │ │   │
│  │  └─────────────────┘                               └──────┬───────┘ │   │
│  └──────────────────────────────────────────────────────────┼─────────┘   │
│                                                             │             │
│                                                             │             │
│  ┌──────────────────────────────────────────────────────────▼─────────┐   │
│  │                    Organic UI Visual Layer (C008)                  │   │
│  │                                                                     │   │
│  │  ┌────────────────┐    ┌──────────────────┐    ┌──────────────┐   │   │
│  │  │ Design Tokens  │    │  Motion Presets  │    │ Metaball     │   │   │
│  │  │  (tokens.ts)   │───▶│   (motion.ts)    │───▶│   System     │   │   │
│  │  │                │    │                  │    │ (SVG Goo)    │   │   │
│  │  └────────────────┘    └──────────────────┘    └──────┬───────┘   │   │
│  │                                                       │             │   │
│  │  ┌──────────────────────────────────────────────────▼─────────┐   │   │
│  │  │                    Voice Nucleus Component                  │   │   │
│  │  │  ┌────────────────┐    ┌──────────────────┐                │   │   │
│  │  │  │ Platform-Aware │    │   Pulse/Drift     │                │   │   │
│  │  │  │   Sizing       │───▶│   Animations     │                │   │   │
│  │  │  │ (160px/72px)   │    │   (Framer Motion) │                │   │   │
│  │  │  └────────────────┘    └──────────────────┘                │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │              Primitive Components (surfaces.tsx)              │   │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────────────┐              │   │   │
│  │  │  │  Cell   │  │ Nucleus │  │  StreamText     │              │   │   │
│  │  │  │ (glass) │  │ (circle)│  │ (animation)     │              │   │   │
│  │  │  └─────────┘  └─────────┘  └─────────────────┘              │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    CSS & Tailwind Integration                       │   │
│  │  ┌────────────────┐    ┌──────────────────┐    ┌──────────────┐   │   │
│  │  │ CSS Variables  │───▶│  Tailwind Config  │───▶│  Styled UI   │   │   │
│  │  │ (globals.css)  │    │ (tailwind.config) │    │  Components  │   │   │
│  │  └────────────────┘    └──────────────────┘    └──────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Layer Structure (Frontend)

```
frontend/
├── design/                 # Design system (single source of truth)
│   ├── tokens.ts           # All design constants (color, space, timing, etc.)
│   ├── motion.ts           # Reusable motion presets (mitosis, pulse, drift, etc.)
│   └── surfaces.tsx        # Primitive components (Cell, Nucleus, StreamText)
├── components/
│   ├── ui/
│   │   ├── voice-nucleus/  # Voice button component (160px/72px)
│   │   │   ├── VoiceButton.tsx
│   │   │   └── Nucleus.tsx  # Primitive component
│   │   ├── metaball/       # Metaball system
│   │   │   ├── MetaballCanvas.tsx
│   │   │   └── physics.ts   # Spring physics engine
│   │   └── widgets/        # Widget components (from C007)
│   │       ├── MarkdownWidget.tsx
│   │       ├── CardWidget.tsx
│   │       └── ...
│   └── agent/
│       ├── ui.tsx          # Widget registry (colocated with graph.py)
│       └── graph.ts        # LangGraph state (Python backend)
├── styles/
│   └── globals.css         # CSS variables (auto-generated from tokens)
├── tailwind.config.js      # Tailwind extends tokens
└── package.json            # Dependencies (Framer Motion, etc.)
```

### 1.3 Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Widget Rendering Flow                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Backend emits widget via LangGraph:                                     │
│                                                                             │
│     Python Backend (C003)                                                   │
│        │                                                                    │
│        │  push_ui_message(                                                  │
│        │    "card",                                                         │
│        │    {"title": "...", "content": "..."},                             │
│        │    message=message                                                 │
│        │  )                                                                 │
│        │                                                                    │
│        ▼                                                                    │
│     LangGraph State (ui_message_reducer)                                    │
│        │                                                                    │
│        │  WebSocket / HTTP Stream                                            │
│        │                                                                    │
│        ▼                                                                    │
│                                                                             │
│  2. Frontend receives widget:                                               │
│                                                                             │
│     Frontend (C007)                                                         │
│        │                                                                    │
│        │  useStream() receives ui message                                   │
│        │                                                                    │
│        ▼                                                                    │
│     LoadExternalComponent                                                   │
│        │                                                                    │
│        │  Resolves component from ui.tsx registry                           │
│        │                                                                    │
│        ▼                                                                    │
│                                                                             │
│  3. Widget renders with Organic UI:                                         │
│                                                                             │
│     Widget Component (C008)                                                 │
│        │                                                                    │
│        │  Uses tokens from design/tokens.ts                                 │
│        │  Uses motion from design/motion.ts                                 │
│        │  Renders with surfaces.tsx primitives                              │
│        │                                                                    │
│        ▼                                                                    │
│     Metaball System                                                         │
│        │                                                                    │
│        │  Widget position/radius added to metaball blob list               │
│        │  SVG goo filter renders merging effect                              │
│        │  Platform-aware blur (16px desktop, 12px mobile)                   │
│        │                                                                    │
│        ▼                                                                    │
│                                                                             │
│  4. Voice Nucleus spawns widgets:                                           │
│                                                                             │
│     Voice Nucleus (C008)                                                    │
│        │                                                                    │
│        │  User speaks → Active state (pulse animation)                      │
│        │  AI responds → Mitosis animation (widget spawns)                   │
│        │  Idle → Drift animation (breathing motion)                         │
│        │                                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow

### 2.1 Token Flow

```
design/tokens.ts (Single Source of Truth)
        │
        ├──▶ globals.css (CSS Variables)
        │       │
        │       └──▶ Direct CSS access (var(--void), var(--enzyme))
        │
        ├──▶ tailwind.config.js (Tailwind Extension)
        │       │
        │       └──▶ Utility classes (bg-void, text-enzyme)
        │
        └──▶ components (TypeScript Imports)
                │
                └──▶ Direct access (tokens.color.void, tokens.timing.spawn)
```

### 2.2 Event Flow (Widget Spawning)

```
User speaks
    │
    ▼
Voice Nucleus → Active state (pulse animation)
    │
    ▼
Audio captured → WebSocket → Backend
    │
    ▼
Backend processes (DSPy ReAct)
    │
    ▼
Backend emits widgets → push_ui_message("card", {...})
    │
    ▼
Frontend receives → ui_message_reducer updates state.ui
    │
    ▼
LoadExternalComponent renders widget
    │
    ▼
Widget spawns with mitosis animation (from motion.mitosis)
    │
    ▼
Widget position added to metaball blob list
    │
    ▼
Metaball system renders SVG goo filter
    │
    ▼
Organic merging effect visible (platform-aware blur)
```

---

## 3. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| **Metaball Implementation** | SVG goo filter | WebGL, Canvas | Works on all platforms, GPU-accelerated, lightweight |
| **Platform-Aware Blur** | 16px desktop, 12px mobile | Fixed blur, disabled on mobile | 25% less GPU load on mobile, maintains visual consistency |
| **Blob Limits** | 12 desktop, 6 mobile | No limits, fixed limit | Prevents performance degradation, adapts to device |
| **Physics Simplification** | Mobile: attraction only | Full physics everywhere | Saves CPU on mobile, maintains organic feel |
| **Token System** | Single TypeScript file | Multiple files, CSS-only | Type-safe, single source of truth, prevents drift |
| **Motion Library** | Framer Motion | CSS animations, React Spring | Industry standard, TypeScript support, declarative API |
| **Component Colocation** | ui.tsx next to graph.py | Separate UI directory | Industry standard (LangSmith), state awareness |
| **Graceful Degradation** | Auto-disable at FPS <20 | Hard requirement, no fallback | Ensures usability on low-end devices |
| **Biological Naming** | Nucleus, cell, enzyme, mitosis | Generic names | Conveys "living organism" concept, self-documenting |
| **Accessibility** | Keyboard, screen reader, reduced motion | Visual-only | WCAG AA compliance, inclusive design |

---

## 4. Tradeoff Analysis

### 4.1 Approach A: SVG Goo Filter (CHOSEN)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐⭐ | Simple SVG markup, no complex shaders |
| Performance | ⭐⭐⭐ | GPU-accelerated, platform-aware optimization |
| Compatibility | ⭐⭐⭐ | Works on all modern browsers (Chrome 90+, Safari 14+, Firefox 88+, Edge 90+) |
| Maintainability | ⭐⭐⭐ | Easy to understand, modify, debug |

**Pros**:
- GPU-accelerated (hardware acceleration built into SVG filters)
- Platform-aware optimization (12px blur on mobile vs 16px on desktop)
- Simple implementation (<100 lines of code)
- Works on all platforms (desktop, tablet, mobile)
- Graceful degradation (fallback to circles if not supported)

**Cons**:
- Slightly more GPU usage than CSS-only approach (mitigated by platform-aware blur)
- Requires performance monitoring (auto-disable at FPS <20)

### 4.2 Approach B: WebGL Metaballs

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐ | Complex shader setup, boilerplate |
| Performance | ⭐⭐⭐⭐ | Best performance, direct GPU control |
| Compatibility | ⭐⭐ | Older devices may not support WebGL 2 |
| Maintainability | ⭐⭐ | Requires GLSL knowledge, harder to debug |

**Pros**:
- Maximum performance (direct GPU control)
- More advanced effects (custom shaders)

**Cons**:
- Overkill for this use case (SVG goo filter is sufficient)
- Higher complexity (shader setup, boilerplate)
- Harder to maintain (GLSL knowledge required)
- Compatibility issues on older devices

### 4.3 Approach C: Canvas 2D Metaballs

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐ | Manual pixel manipulation, complex |
| Performance | ⭐⭐ | CPU-bound, slower than GPU approaches |
| Compatibility | ⭐⭐⭐ | Works on most browsers (Canvas API widely supported) |
| Maintainability | ⭐ | Complex pixel manipulation logic |

**Pros**:
- Widely supported (Canvas API available everywhere)

**Cons**:
- CPU-bound (slower than GPU approaches)
- Complex pixel manipulation (thresholding, blurring)
- Harder to maintain (manual loop over pixels)

### 4.4 Decision: SVG Goo Filter

**Rationale**:
- **Best balance** of simplicity, performance, and compatibility
- **Platform-aware optimization** mitigates GPU usage concerns (12px blur on mobile)
- **GPU-accelerated** by default (modern browsers hardware-accelerate SVG filters)
- **Simple implementation** (<100 lines vs 500+ for WebGL)
- **Graceful degradation** built-in (fallback to circles)
- **Proven technology** (used in production by many companies)

**Rejection of Alternatives**:
- **WebGL**: Overkill, too complex, compatibility issues
- **Canvas**: CPU-bound, slower, more complex than SVG

---

## 5. Implementation Details

### 5.1 Key Classes/Modules

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| **design/tokens.ts** | Single source of truth for all design constants | None (frozen constants) |
| **design/motion.ts** | Reusable motion presets (mitosis, pulse, drift, etc.) | tokens.ts (timing, easing, shadow) |
| **design/surfaces.tsx** | Primitive components (Cell, Nucleus, StreamText) | tokens.ts, motion.ts, Framer Motion |
| **components/ui/voice-nucleus/VoiceButton.tsx** | Voice button with platform-aware sizing | tokens.ts, motion.ts, surfaces.tsx |
| **components/ui/metaball/MetaballCanvas.tsx** | SVG goo filter + blob rendering | tokens.ts, capability functions |
| **components/ui/metaball/physics.ts** | Spring physics engine (attraction, repulsion) | tokens.ts (metaball physics constants) |
| **components/agent/ui.tsx** | Widget registry (colocated with graph.py) | All widget components |
| **styles/globals.css** | CSS variables (auto-generated from tokens) | tokens.ts (via build script) |
| **tailwind.config.js** | Tailwind extends tokens | tokens.ts (via build script) |

### 5.2 Port Assignments

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| **Frontend (Next.js)** | 3000 | HTTP | Main frontend application (from C007) |
| **LangGraph Server** | 2024 | HTTP | Backend graph execution (from C003) |
| **Voice API** | 8018 | HTTP | Voice endpoints (from C004) |
| **Voice WebSocket** | 8019 | WS | Voice streaming (from C004) |

**Note**: C008 uses existing ports from C007 and C004. No new ports required.

### 5.3 Storage Schema

**Note**: C008 is frontend-only with no storage requirements.

### 5.4 File Structure (Implementation)

```
frontend/
├── design/
│   ├── tokens.ts          # ~180 lines (all design constants)
│   ├── motion.ts          # ~150 lines (9 presets + stagger)
│   └── surfaces.tsx       # Split into multiple files:
│       ├── Cell.tsx       # ~60 lines
│       ├── Nucleus.tsx    # ~80 lines
│       └── StreamText.tsx # ~40 lines
├── components/
│   ├── ui/
│   │   ├── voice-nucleus/
│   │   │   ├── VoiceButton.tsx    # ~100 lines
│   │   │   └── Nucleus.tsx        # ~80 lines (primitive)
│   │   ├── metaball/
│   │   │   ├── MetaballCanvas.tsx # ~100 lines
│   │   │   └── physics.ts         # ~80 lines
│   │   └── widgets/               # From C007
│   │       ├── MarkdownWidget.tsx # ~80 lines each
│   │       ├── CardWidget.tsx
│   │       └── ... (10 more)
│   └── agent/
│       ├── ui.tsx                  # Widget registry (~50 lines)
│       └── graph.ts                # LangGraph integration (~100 lines)
├── styles/
│   └── globals.css      # ~200 lines (CSS variables)
├── tailwind.config.js   # ~80 lines (extends tokens)
└── package.json         # Dependencies (Framer Motion, etc.)
```

**Total Estimated Lines**: ~1,500 lines (excluding C007 widgets)

---

## 6. Security Considerations

| Concern | Mitigation |
|---------|------------|
| **XSS in Widget Props** | LangGraph server-driven UI ensures props are backend-generated, not user-input |
| **CSS Injection** | All tokens are frozen constants, no user-generated CSS |
| **SVG Filter Abuse** | Filter is self-contained, no external resources |
| **Framer Motion Vulnerabilities** | Use pinned version, monitor for security updates |
| **WebSocket Hijacking** | Use WSS (secure WebSocket) in production |

**Note**: C008 is primarily a visual layer with minimal security concerns. Main security is handled by C007 (LangGraph server-driven UI) and C004 (voice WebSocket).

---

## 7. Performance Considerations

| Concern | Mitigation |
|---------|------------|
| **GPU Usage (Metaballs)** | Platform-aware blur (12px mobile, 16px desktop), blob limits (6 mobile, 12 desktop) |
| **CPU Usage (Physics)** | Simplified physics on mobile (attraction only), requestAnimationFrame throttling (30fps mobile, 60fps desktop) |
| **Bundle Size (Framer Motion)** | Tree-shaking (import only used presets), consider lighter alternative if bundle >50KB |
| **Animation Jank** | Auto-disable when FPS <20 for 3 consecutive seconds, fallback to circles |
| **Memory Leaks** | Cleanup event listeners on unmount, limit metaball blob count |
| **SSR Performance** | No `window` access during render (SSR-safe), capability checks guard browser APIs |
| **Network Latency** | Widgets stream via WebSocket (no blocking), progressive rendering (mitosis animation) |

**Performance Targets**:
- Desktop: ≥60fps with 12 blobs
- Mobile: ≥30fps with 6 blobs
- Bundle size: <50KB (gzipped) for design system
- First paint: <1s (voice nucleus visible)
- Time to interactive: <3s (full UI responsive)

---

## 8. Accessibility Considerations

| Concern | Mitigation |
|---------|------------|
| **Motion Sensitivity** | Respect `prefers-reduced-motion`, disable all animations when true |
| **Keyboard Navigation** | Voice nucleus accessible via Tab, Space key toggles voice state |
| **Screen Reader** | ARIA labels accurate ("Start speaking" / "Stop speaking"), ARIA pressed reflects state |
| **Touch Targets** | Voice nucleus 72px (well above 44px minimum), all interactive elements meet WCAG |
| **Color Contrast** | WCAG AA compliance verification during implementation, adjust token values if needed |
| **Focus Indicators** | `focus-visible:ring-2 ring-enzyme` for clear focus state |

**WCAG 2.1 AA Compliance**:
- Color contrast: ≥4.5:1 for normal text, ≥3:1 for large text
- Touch targets: ≥44x44px (voice nucleus 72px satisfies)
- Keyboard accessibility: Full functionality without mouse
- Screen reader: Semantic HTML, ARIA labels, live regions for dynamic content

---

**Next Artifact**: tasks.md
