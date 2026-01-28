# Scan Artifact: c008-organic-ui

**Generated**: 2026-01-29
**Change**: c008-organic-ui
**Schema**: spec-factory v1.0.0

---

## 1. LLD Synthesis

### 1.1 Relevant LLD Documents

| Document | Path | Relevance |
|----------|------|-----------|
| Organic UI Design System | `/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/agentx_organic_ui_design_system.md` | Primary LLD - design tokens, metaball specs, voice nucleus |
| C003 Agent Pipeline Design | `/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c003-agent-pipeline/design.md` | LangGraph server-driven UI integration |
| C007 Frontend Architecture | `/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c007-frontend-architecture/design.md` | Component colocation, LoadExternalComponent pattern |

### 1.2 Locked Definitions from LLD

#### Design Tokens (Locked from agentx_organic_ui_design_system.md:18-210)

```typescript
// Color Palette (Locked)
void: '#0A0A0A'           // Deep space background
membrane: '#141414'        // Primary surface
cytoplasm: '#1C1C1C'       // Secondary surface
organelle: '#252525'       // Tertiary surface
nucleus: 'rgba(255,255,255,0.96)'     // Primary text
protein: 'rgba(255,255,255,0.72)'     // Secondary text
ghost: 'rgba(255,255,255,0.38)'       // Tertiary text
enzyme: '#00D9FF'         // Primary action (cyan life)
enzymeSoft: 'rgba(0,217,255,0.12)'
enzymeGlow: 'rgba(0,217,255,0.24)'
mitosis: '#00FF88'        // Success/growth
apoptosis: '#FF4444'      // Error/death

// Radius (Locked)
cell: '50%'               // Perfect circle
bubble: '42%'             // Slightly organic
lg: '32px'
md: '24px'
sm: '16px'
xs: '12px'

// Spacing (Locked - 8px grid)
nucleus: 4
cell: 8
tissue: 16
organ: 24
organism: 32
colony: 48
ecosystem: 64

// Shadows (Locked)
cell: '0 2px 8px rgba(0,0,0,0.3)'
float: '0 8px 32px rgba(0,0,0,0.4)'
deep: '0 16px 64px rgba(0,0,0,0.5)'
glow: '0 0 24px rgba(0,217,255,0.3)'
pulse: '0 0 48px rgba(0,217,255,0.5)'

// Blur (Locked)
light: '8px'
medium: '16px'
heavy: '24px'

// Timing (Locked - biology-inspired)
instant: 80ms
quick: 150ms
normal: 240ms
spawn: 380ms
morph: 520ms
drift: 2400ms

// Easing (Locked - organic motion curves)
cell: [0.25, 0.1, 0.25, 1]
elastic: [0.68, -0.55, 0.265, 1.55]
anticipate: [0.22, 1, 0.36, 1]
exit: [0.4, 0, 0.2, 1]

// Metaball Physics (Locked)
threshold: 0.5
viscosity: 0.3
attraction: 0.02
repulsion: 0.05
maxSpeed: 2

// Mobile Optimizations (Locked)
mobileBlur: 12            // Lower blur for mobile (vs 16 desktop)
mobileMaxBlobs: 6         // Limit concurrent blobs on mobile
radius.voice: 160         // Central voice nucleus (desktop)
radius.voiceMobile: 72    // Smaller on mobile

// Widget Sizes (Locked)
micro: { w: 180, h: 120 }
small: { w: 280, h: 200 }
medium: { w: 380, h: 280 }
large: { w: 520, h: 380 }
hero: { w: 720, h: 480 }

// Z-Index Layers (Locked)
bg: 0
metaball: 1
surface: 10
widget: 20
float: 30
voice: 40
modal: 50
toast: 60

// Breakpoints (Locked)
mobile: 640
tablet: 1024
desktop: 1440
wide: 1920
```

#### Widget Type Enum (Locked)

```typescript
type WidgetType =
  | 'markdown'      // Rich text content
  | 'card'          // Simple info card
  | 'form'          // Input form
  | 'progress'      // Progress indicator
  | 'action'        // Action button
  | 'confirmation'  // Yes/no dialog
  | 'image'         // Single image
  | 'gallery'       // Image grid
  | 'chart'         // Data visualization
  | 'searchResult'  // Search result item
  | 'hopProgress'   // Active state tracking
  | 'citationCard'  // Citation with source
```

#### Motion Presets (Locked from agentx_organic_ui_design_system.md:214-349)

```typescript
mitosis: {
  initial: { scale: 0, opacity: 0, filter: 'blur(12px)' },
  animate: { scale: 1, opacity: 1, filter: 'blur(0px)' },
  exit: { scale: 0.8, opacity: 0, filter: 'blur(8px)' },
  transition: { duration: 0.38, ease: [0.68, -0.55, 0.265, 1.55] }
}

pulse: {
  animate: {
    scale: [1, 1.08, 1],
    boxShadow: [glow, pulse, glow]
  },
  transition: { duration: 1.4, repeat: Infinity }
}

drift: {
  animate: { y: [0, -8, 0], x: [0, 4, 0] },
  transition: { duration: 2.4, repeat: Infinity }
}
```

---

## 2. Codebase Exploration (opsx:explore)

### 2.1 Exploration Topics

```
1. Organic UI design tokens and metaball physics
2. Voice nucleus component (desktop 160px, mobile 72px)
3. Platform-aware blur (16px desktop, 12px mobile)
4. Widget spawning with mitosis animation
5. LangGraph server-driven UI integration (from C007)
6. Component colocation pattern (ui.tsx next to graph.py)
7. Mobile performance optimizations (6 blob limit, simplified physics)
```

### 2.2 File Inventory

#### Backend Files
| File | Lines | Purpose |
|------|-------|---------|
| `docs/engineering/agentx_organic_ui_design_system.md` | 1116 | Primary LLD - design tokens, metaball specs |
| `openspec/changes/c003-agent-pipeline/design.md` | 450+ | LangGraph server-driven UI architecture |
| `openspec/changes/c007-frontend-architecture/design.md` | 380+ | Component colocation, LoadExternalComponent |

#### Frontend Files (References)
| File | Lines | Purpose |
|------|-------|---------|
| `prototypes/R014_ui_showcase/frontend/components/ui/central-island.tsx` | 229 | Reference: Central voice nucleus pattern |
| `prototypes/R014_ui_showcase/frontend/types/widget-types.ts` | 120+ | Reference: Widget type definitions |

---

## 3. Patterns Discovered

### 3.1 Architectural Patterns

**1. Bio-Inspired Metaphor System**
- All UI elements named after biological concepts (nucleus, cell, membrane, enzyme)
- Central "voice nucleus" spawns widgets via "mitosis" animation
- Organic motion curves mimic cellular behavior

**2. Platform-Aware Metaballs (Universal)**
- Desktop: 16px blur, 12 concurrent blobs, full physics (attraction + repulsion)
- Mobile: 12px blur, 6 concurrent blobs, simplified physics (attraction only)
- Graceful degradation: auto-disable on struggling devices

**3. Single Source of Truth Design Tokens**
- `design/tokens.ts` contains ALL design constants
- TypeScript tokens → CSS variables → Tailwind config
- Change one file, entire UI updates

**4. Voice-First Widget Spawning**
- All widgets emerge from central voice nucleus
- Mitosis animation: start as tiny circles, morph into rounded rectangles
- Spring physics move widgets to anchor positions

### 3.2 Code Patterns

**1. Capability Detection Pattern**
```typescript
export const capability = {
  isMobile: () => window.innerWidth < 1024 || navigator.userAgent.match(/iPhone|Android/i),
  prefersReducedMotion: () => window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  getMetaballConfig: () => ({
    enabled: !prefersReducedMotion(),
    blur: isMobile() ? 12 : 16,
    maxBlobs: isMobile() ? 6 : 12,
    simplifyPhysics: isMobile()
  })
}
```

**2. SVG Goo Filter Pattern (Universal)**
```typescript
<filter id="goo">
  <feGaussianBlur in="SourceGraphic" stdDeviation={config.blur} result="blur" />
  <feColorMatrix in="blur" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 24 -10" />
</filter>
```

**3. Component Colocation (from C007)**
- `ui.tsx` placed next to `graph.py` in backend code
- LangGraph `push_ui_message()` emits widgets
- Frontend `LoadExternalComponent` renders them

**4. Motion Preset Reusability**
- All animations defined in `design/motion.ts`
- Components reference presets by name (`mitosis`, `pulse`, `drift`)
- Consistent timing across entire UI

### 3.3 Anti-Patterns to Avoid

**1. Don't Disable Metaballs on Mobile**
- ❌ Old approach: "Metaballs too heavy for mobile, disable entirely"
- ✅ New approach: "Optimize metaballs per platform (12px blur, 6 blobs)"

**2. Don't Use Fixed Widget Counts**
- ❌ Old approach: "Max 12 widgets always"
- ✅ New approach: "6 widgets on mobile, 12 on desktop (capability-based)"

**3. Don't Hardcode Platform Detection**
- ❌ Old approach: `if (navigator.userAgent === 'iPhone')`
- ✅ New approach: `capability.isMobile()` (viewport + UA + feature detection)

**4. Don't Separate Mobile/Desktop Implementations**
- ❌ Old approach: "metaballs-desktop.ts" and "metaballs-mobile.ts"
- ✅ New approach: Single metaball system with platform-aware config

**5. Don't Ignore Reduced Motion Preference**
- ❌ Old approach: "Force animations always"
- ✅ New approach: Respect `prefers-reduced-motion: reduce`

---

## 4. Reference Analysis

### 4.1 Mimicus Patterns (Copy Concepts, Not Names)

| Concept | Mimicus Pattern | Intended Use |
|---------|-----------------|--------------|
| Clean Architecture | core/, domain/, application/, infrastructure/, presentation/ | Not applicable for frontend UI specs |
| Repository | ABC base class + implementations | Not applicable for frontend UI specs |
| Entity | @dataclass with business methods | Not applicable for frontend UI specs |
| Use Case | Single-purpose classes with execute() | Not applicable for frontend UI specs |

**Note**: C008 is a frontend UI change, not backend. Mimicus patterns don't directly apply.

### 4.2 R014 Reference (Concepts Only)

| Concept | R014 Approach | Improved Approach |
|---------|---------------|-------------------|
| **Central Voice Nucleus** | Fixed-size central island (229 lines in central-island.tsx) | Platform-aware sizing (160px desktop, 72px mobile) with pulse animation |
| **Widget Types** | 12 widget types in widget-types.ts | Same 12 types, but emitted via LangGraph `push_ui_message()` not WebSocket callbacks |
| **Layout** | Rigid anchor positions | Organic spring physics with metaball merging |
| **Mobile** | Responsive but same blur | Platform-aware blur (12px vs 16px) + blob limits (6 vs 12) |
| **Animations** | CSS transitions | Framer Motion with elastic easing + mitosis preset |
| **Component Colocation** | Separate UI components directory | ui.tsx colocated with graph.py (C007 pattern) |

**R014 Problems Fixed**:
- R014 had no metaball merging (widgets were separate bubbles)
- R014 used fixed blur on all devices (performance issues on mobile)
- R014 had no blob limits (could spawn infinite widgets)
- R014 didn't respect `prefers-reduced-motion`

**C008 Improvements**:
- Universal metaballs with platform-aware optimization
- Intelligent blob limits (6 mobile, 12 desktop)
- Graceful degradation (auto-disable on struggling devices)
- Full accessibility support (reduced motion, keyboard, screen reader)

---

## 5. Key Files for This Change

```
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/agentx_organic_ui_design_system.md
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c003-agent-pipeline/design.md
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c007-frontend-architecture/design.md
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/frontend/components/ui/central-island.tsx
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/frontend/types/widget-types.ts
```

---

**Next Artifact**: extract.md
