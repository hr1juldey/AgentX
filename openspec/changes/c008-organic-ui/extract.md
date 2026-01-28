# Extract Artifact: c008-organic-ui

**Generated**: 2026-01-29
**Change**: c008-organic-ui
**Schema**: spec-factory v1.0.0

---

## 1. Pattern Catalog

### 1.1 Architectural Patterns

| Pattern | Source | Description | Apply? |
|---------|--------|-------------|--------|
| **Bio-Inspired Metaphor System** | agentx_organic_ui_design_system.md | All UI elements named after biological concepts (nucleus, cell, membrane, enzyme) | ✅ |
| **Platform-Aware Metaballs** | agentx_organic_ui_design_system.md | Universal metaball system with platform-aware optimization (16px blur desktop, 12px mobile) | ✅ |
| **Single Source of Truth Tokens** | agentx_organic_ui_design_system.md | `design/tokens.ts` contains ALL design constants → CSS variables → Tailwind config | ✅ |
| **Voice-First Widget Spawning** | agentx_organic_ui_design_system.md | Central voice nucleus spawns widgets via mitosis animation with spring physics | ✅ |
| **Component Colocation** | C007 design.md | ui.tsx placed next to graph.py in backend code | ✅ |
| **LangGraph Server-Driven UI** | C007 design.md | Backend emits UI via `push_ui_message()`, frontend renders via `LoadExternalComponent` | ✅ |
| **Graceful Degradation** | agentx_organic_ui_design_system.md | Auto-disable metaballs on struggling devices, falls back to clean circles | ✅ |

### 1.2 Code Structure Patterns

| Pattern | Example | Apply? |
|---------|---------|--------|
| **Capability Detection** | `capability.isMobile()`, `capability.getMetaballConfig()` | ✅ |
| **SVG Goo Filter** | `<feGaussianBlur stdDeviation={config.blur} />` | ✅ |
| **Motion Preset Reusability** | `motion.mitosis`, `motion.pulse`, `motion.drift` | ✅ |
| **Widget Protocol** | `type: 'widget'`, `component: WidgetType`, `props: Record<string, any>` | ✅ |
| **Token System** | `tokens.color.void`, `tokens.radius.cell`, `tokens.timing.spawn` | ✅ |
| **Platform-Aware Config** | `blur: isMobile() ? 12 : 16`, `maxBlobs: isMobile() ? 6 : 12` | ✅ |
| **Spring Physics** | `attraction: 0.02`, `repulsion: 0.05`, `viscosity: 0.3` | ✅ |

### 1.3 Naming Patterns (to Avoid from R014)

| R014 Name | Why Avoid | Alternative |
|-----------|-----------|-------------|
| `central-island.tsx` | Too generic, doesn't convey biological metaphor | `voice-nucleus.tsx` |
| `widget-types.ts` | Doesn't indicate LangGraph integration | `widget-protocol.ts` |
| `UiDescriptor` | Descriptor-only pattern replaced by server-driven UI | `push_ui_message()` + `LoadExternalComponent` |
| Hardcoded platform detection (`navigator.userAgent === 'iPhone'`) | Fragile, doesn't handle all mobile devices | `capability.isMobile()` with viewport + UA detection |
| Fixed widget limits (`max 12 widgets`) | Not performance-aware for mobile | Platform-aware limits (6 mobile, 12 desktop) |
| Fixed blur (`16px always`) | Too heavy for mobile GPUs | Platform-aware blur (12px mobile, 16px desktop) |

---

## 2. Specification Drafts

### 2.1 Draft: design-tokens Spec

**Purpose**: Define the single source of truth design token system that powers the entire Organic UI, including colors, spacing, typography, shadows, blur, timing, easing, metaball physics, and platform-aware configurations.

**Scope**:
- **In Scope**:
  - Design token definitions (color, radius, space, shadow, blur, font, timing, easing, metaball, widget, layer)
  - Capability detection (isMobile, prefersReducedMotion, getMetaballConfig)
  - Breakpoint definitions (mobile, tablet, desktop, wide)
  - TypeScript token exports
  - CSS variable generation
  - Tailwind config extension
- **Out of Scope**:
  - Component implementations (Cell, Nucleus, VoiceButton)
  - Motion preset implementations
  - Metaball physics engine
  - Widget spawning logic

**Locked from LLD** (agentx_organic_ui_design_system.md:18-210):

```typescript
export const tokens = {
  color: {
    void: '#0A0A0A',
    membrane: '#141414',
    cytoplasm: '#1C1C1C',
    organelle: '#252525',
    nucleus: 'rgba(255,255,255,0.96)',
    protein: 'rgba(255,255,255,0.72)',
    ghost: 'rgba(255,255,255,0.38)',
    enzyme: '#00D9FF',
    enzymeSoft: 'rgba(0,217,255,0.12)',
    enzymeGlow: 'rgba(0,217,255,0.24)',
    mitosis: '#00FF88',
    apoptosis: '#FF4444',
    glassWeak: 'rgba(255,255,255,0.03)',
    glassMid: 'rgba(255,255,255,0.06)',
    glassStrong: 'rgba(255,255,255,0.09)',
  },
  radius: {
    cell: '50%',
    bubble: '42%',
    lg: '32px',
    md: '24px',
    sm: '16px',
    xs: '12px',
  },
  space: {
    nucleus: 4,
    cell: 8,
    tissue: 16,
    organ: 24,
    organism: 32,
    colony: 48,
    ecosystem: 64,
  },
  shadow: {
    cell: '0 2px 8px rgba(0,0,0,0.3)',
    float: '0 8px 32px rgba(0,0,0,0.4)',
    deep: '0 16px 64px rgba(0,0,0,0.5)',
    glow: '0 0 24px rgba(0,217,255,0.3)',
    pulse: '0 0 48px rgba(0,217,255,0.5)',
  },
  blur: {
    light: '8px',
    medium: '16px',
    heavy: '24px',
  },
  font: {
    family: {
      ui: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", system-ui, sans-serif',
      mono: '"SF Mono", "Fira Code", "Consolas", monospace',
      display: '"SF Pro Display", -apple-system, sans-serif',
    },
    size: {
      xs: '11px',
      sm: '13px',
      base: '15px',
      md: '17px',
      lg: '20px',
      xl: '24px',
      xxl: '32px',
      voice: '48px',
    },
    weight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    leading: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.7,
    },
  },
  timing: {
    instant: 80,
    quick: 150,
    normal: 240,
    spawn: 380,
    morph: 520,
    drift: 2400,
  },
  easing: {
    cell: [0.25, 0.1, 0.25, 1],
    elastic: [0.68, -0.55, 0.265, 1.55],
    anticipate: [0.22, 1, 0.36, 1],
    exit: [0.4, 0, 0.2, 1],
  },
  metaball: {
    threshold: 0.5,
    viscosity: 0.3,
    attraction: 0.02,
    repulsion: 0.05,
    maxSpeed: 2,
    mobileSimplify: true,
    mobileBlur: 12,
    mobileMaxBlobs: 6,
    radius: {
      micro: 32,
      small: 64,
      medium: 96,
      large: 128,
      voice: 160,
      voiceMobile: 72,
    },
  },
  widget: {
    micro: { w: 180, h: 120 },
    small: { w: 280, h: 200 },
    medium: { w: 380, h: 280 },
    large: { w: 520, h: 380 },
    hero: { w: 720, h: 480 },
  },
  layer: {
    bg: 0,
    metaball: 1,
    surface: 10,
    widget: 20,
    float: 30,
    voice: 40,
    modal: 50,
    toast: 60,
  },
}

export const breakpoint = {
  mobile: 640,
  tablet: 1024,
  desktop: 1440,
  wide: 1920,
}

export const capability = {
  isMobile: () => window.innerWidth < breakpoint.tablet || navigator.userAgent.match(/iPhone|iPad|Android/i),
  prefersReducedMotion: () => window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  getMetaballConfig: () => ({
    enabled: !capability.prefersReducedMotion(),
    blur: capability.isMobile() ? tokens.metaball.mobileBlur : 16,
    maxBlobs: capability.isMobile() ? tokens.metaball.mobileMaxBlobs : 12,
    simplifyPhysics: capability.isMobile(),
  }),
}
```

**Requirements**:
1. FR-DT-001: Design tokens MUST be defined in single TypeScript file (`design/tokens.ts`)
2. FR-DT-002: Token values MUST be frozen (no runtime modifications)
3. FR-DT-003: CSS variables MUST be auto-generated from tokens
4. FR-DT-004: Tailwind config MUST extend tokens (not duplicate)
5. FR-DT-005: Capability detection MUST check viewport + UA + features (not just UA)
6. FR-DT-006: `getMetaballConfig()` MUST return platform-aware configuration

**Acceptance Criteria**:
- [ ] All token categories defined (color, radius, space, shadow, blur, font, timing, easing, metaball, widget, layer)
- [ ] CSS variables generated in `globals.css`
- [ ] Tailwind config extends tokens
- [ ] `capability.isMobile()` checks viewport + UA + features
- [ ] `capability.getMetaballConfig()` returns platform-aware config
- [ ] Token values match LLD exactly (no deviations)

---

### 2.2 Draft: metaball-system Spec

**Purpose**: Define the universal metaball system that provides organic fluid merging effects on all platforms with intelligent performance optimization.

**Scope**:
- **In Scope**:
  - SVG goo filter implementation
  - Platform-aware blur (16px desktop, 12px mobile)
  - Spring physics (attraction, repulsion, viscosity)
  - Blob limits (12 desktop, 6 mobile)
  - Performance monitoring and auto-disable
  - Graceful degradation to clean circles
- **Out of Scope**:
  - Widget rendering (widgets provide position/radius)
  - Motion animations (handled by Framer Motion)
  - Layout system (anchor positions, mobile stack)

**Locked from LLD** (agentx_organic_ui_design_system.md:839-932):

```typescript
// SVG Goo Filter
function MetaballCanvas({ widgets }) {
  const config = capability.getMetaballConfig()

  if (!config.enabled) return null // Respect reduced-motion

  return (
    <svg className="absolute inset-0 pointer-events-none" style={{ zIndex: tokens.layer.metaball }}>
      <defs>
        <filter id="goo">
          <feGaussianBlur in="SourceGraphic" stdDeviation={config.blur} result="blur" />
          <feColorMatrix in="blur" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 24 -10" />
        </filter>
      </defs>
      <g filter="url(#goo)">
        {widgets.slice(0, config.maxBlobs).map(w => (
          <circle key={w.id} cx={w.x} cy={w.y} r={w.radius} fill="rgba(255,255,255,0.06)" />
        ))}
      </g>
    </svg>
  )
}

// Physics (Simplified for Mobile)
function updateWidgetPhysics(widget, allWidgets, delta) {
  const config = capability.getMetaballConfig()

  // Spring toward anchor point (universal)
  const anchor = anchors[widget.anchor]
  const dx = anchor.x - widget.x
  const dy = anchor.y - widget.y
  widget.vx += dx * tokens.metaball.attraction
  widget.vy += dy * tokens.metaball.attraction

  // Repulsion (skip on mobile for performance)
  if (!config.simplifyPhysics) {
    allWidgets.forEach(other => {
      if (other.id === widget.id) return
      const dist = distance(widget, other)
      if (dist < 200) {
        const force = tokens.metaball.repulsion / dist
        widget.vx -= force * (other.x - widget.x)
        widget.vy -= force * (other.y - widget.y)
      }
    })
  }

  // Apply friction
  widget.vx *= (1 - tokens.metaball.viscosity)
  widget.vy *= (1 - tokens.metaball.viscosity)

  // Update position
  widget.x += widget.vx * delta
  widget.y += widget.vy * delta
}
```

**Requirements**:
1. FR-MS-001: Metaballs MUST use SVG goo filter (works on all platforms)
2. FR-MS-002: Blur MUST be platform-aware (16px desktop, 12px mobile)
3. FR-MS-003: Blob count MUST be limited (12 desktop, 6 mobile)
4. FR-MS-004: Physics MUST be simplified on mobile (attraction only)
5. FR-MS-005: System MUST auto-disable if FPS drops below 20
6. FR-MS-006: Reduced motion preference MUST be respected
7. FR-MS-007: Graceful degradation MUST fall back to clean circles

**Acceptance Criteria**:
- [ ] SVG goo filter renders metaball merging effect
- [ ] Platform-aware blur applied (16px desktop, 12px mobile)
- [ ] Blob limits enforced (12 desktop, 6 mobile)
- [ ] Physics simplified on mobile (no repulsion)
- [ ] Auto-disable triggers when FPS < 20
- [ ] `prefers-reduced-motion` disables metaballs
- [ ] Graceful degradation to circles when disabled

---

### 2.3 Draft: voice-nucleus Spec

**Purpose**: Define the central voice interface component that serves as the visual and interaction hub for all voice operations, spawning widgets via mitosis animation.

**Scope**:
- **In Scope**:
  - Voice nucleus component (160px desktop, 72px mobile)
  - Platform-aware positioning (center desktop, bottom-center mobile)
  - Pulse animation when active
  - Drift animation when idle
  - Mitosis animation for widget spawning
  - Touch target compliance (minimum 44px)
  - Accessibility (keyboard, screen reader, reduced motion)
- **Out of Scope**:
  - WebSocket connection (C004 voice-streaming)
  - Audio capture/playback (C004 voice-streaming)
  - Transcript rendering (handled by transcript widget)
  - Widget layout system (anchors, mobile stack)

**Locked from LLD** (agentx_organic_ui_design_system.md:657-703, 1006-1056):

```typescript
// Desktop: 160px circular nucleus at viewport center
// Mobile: 72px circular nucleus at bottom-center (thumb-friendly)

export function VoiceButton({ active, onToggle }: { active: boolean, onToggle: () => void }) {
  const isMobile = capability.isMobile()
  const size = isMobile ? 72 : 160

  return (
    <motion.button
      onClick={onToggle}
      onKeyDown={(e) => e.key === ' ' && onToggle()}
      className="focus:outline-none focus-visible:ring-2 focus-visible:ring-enzyme"
      style={{
        position: isMobile ? 'fixed' : 'absolute',
        bottom: isMobile ? 24 : '50%',
        left: '50%',
        transform: isMobile ? 'translateX(-50%)' : 'translate(-50%, 50%)',
      }}
      aria-label={active ? "Stop speaking" : "Start speaking"}
      aria-pressed={active}
      {...motionPresets.lift}
      {...motionPresets.compress}
    >
      <Nucleus size={size} active={active}>
        <motion.div
          className="w-8 h-8 rounded-cell bg-enzyme"
          animate={active ? { scale: [1, 1.2, 1] } : {}}
          transition={{ duration: 0.6, repeat: active ? Infinity : 0 }}
        />
      </Nucleus>
    </motion.button>
  )
}

// Nucleus primitive
export function Nucleus({ size = 160, active = false, children, ...props }) {
  return (
    <motion.div
      className="rounded-cell bg-organelle backdrop-blur-heavy border border-white/[0.09]"
      style={{
        width: size,
        height: size,
        boxShadow: active ? tokens.shadow.pulse : tokens.shadow.float,
      }}
      animate={active ? motion.pulse.animate : undefined}
      transition={active ? motion.pulse.transition : undefined}
      {...props}
    >
      <div className="w-full h-full flex items-center justify-center">
        {children}
      </div>
    </motion.div>
  )
}
```

**Requirements**:
1. FR-VN-001: Nucleus size MUST be platform-aware (160px desktop, 72px mobile)
2. FR-VN-002: Position MUST be platform-aware (center desktop, bottom-center mobile)
3. FR-VN-003: Active state MUST show pulse animation
4. FR-VN-004: Idle state MUST show drift animation
5. FR-VN-005: Touch target MUST be minimum 44px (72px satisfies this)
6. FR-VN-006: Keyboard accessible (Space to toggle)
7. FR-VN-007: Screen reader label MUST be accurate
8. FR-VN-008: Reduced motion preference MUST disable animations

**Acceptance Criteria**:
- [ ] Nucleus renders at 160px on desktop, 72px on mobile
- [ ] Position center (desktop) or bottom-center (mobile)
- [ ] Pulse animation when active
- [ ] Drift animation when idle
- [ ] Space key toggles voice state
- [ ] ARIA label accurate ("Start speaking" / "Stop speaking")
- [ ] Animations respect `prefers-reduced-motion`

---

### 2.4 Draft: motion-presets Spec

**Purpose**: Define reusable motion presets that provide consistent animation behavior across all UI components, following biological metaphors (mitosis, pulse, drift).

**Scope**:
- **In Scope**:
  - Mitosis preset (widget spawning)
  - Pulse preset (voice active state)
  - Drift preset (idle floating)
  - Lift preset (hover)
  - Compress preset (tap)
  - Drag preset (dragging)
  - Morph preset (shape transformation)
  - Stream preset (text streaming)
  - Interrupt preset (attention grab)
  - Stagger presets (container/item)
- **Out of Scope**:
  - Physics simulation (metaball-system spec)
  - Component implementations (voice-nucleus spec)

**Locked from LLD** (agentx_organic_ui_design_system.md:214-349):

```typescript
export const motion = {
  // Cell division - widget spawning
  mitosis: {
    initial: { scale: 0, opacity: 0, filter: 'blur(12px)' },
    animate: { scale: 1, opacity: 1, filter: 'blur(0px)' },
    exit: { scale: 0.8, opacity: 0, filter: 'blur(8px)' },
    transition: { duration: tokens.timing.spawn / 1000, ease: tokens.easing.elastic },
  },

  // Nucleus pulse - voice active state
  pulse: {
    animate: {
      scale: [1, 1.08, 1],
      boxShadow: [tokens.shadow.glow, tokens.shadow.pulse, tokens.shadow.glow],
    },
    transition: { duration: 1.4, repeat: Infinity, ease: 'easeInOut' },
  },

  // Idle floating - breathing motion
  drift: {
    animate: { y: [0, -8, 0], x: [0, 4, 0] },
    transition: { duration: tokens.timing.drift / 1000, repeat: Infinity, ease: 'easeInOut' },
  },

  // Hover - subtle lift
  lift: {
    whileHover: { scale: 1.02, y: -2, boxShadow: tokens.shadow.float },
    transition: { duration: tokens.timing.quick / 1000 },
  },

  // Press - quick compression
  compress: {
    whileTap: { scale: 0.96 },
    transition: { duration: tokens.timing.instant / 1000 },
  },

  // Drag - emphasized state
  drag: {
    whileDrag: {
      scale: 1.05,
      boxShadow: tokens.shadow.deep,
      cursor: 'grabbing',
      zIndex: tokens.layer.float + 10,
    },
  },

  // Morph - shape transformation
  morph: {
    transition: { duration: tokens.timing.morph / 1000, ease: tokens.easing.cell },
  },

  // Text streaming - progressive reveal
  stream: {
    initial: { opacity: 0, x: -8 },
    animate: { opacity: 1, x: 0 },
    transition: { duration: tokens.timing.quick / 1000, ease: tokens.easing.anticipate },
  },

  // Interrupt signal - attention grab
  interrupt: {
    initial: { scale: 0.8, opacity: 0 },
    animate: { scale: [0.8, 1.1, 1], opacity: 1 },
    transition: { duration: 0.4, ease: tokens.easing.elastic },
  },
}

// Stagger children animations
export const stagger = {
  container: {
    animate: {
      transition: { staggerChildren: 0.08, delayChildren: 0.1 },
    },
  },
  item: motion.stream,
}
```

**Requirements**:
1. FR-MP-001: All presets MUST reference tokens (no hardcoded values)
2. FR-MP-002: Timing MUST follow biological metaphors (spawn 380ms, pulse 1.4s, drift 2.4s)
3. FR-MP-003: Easing MUST use organic curves (elastic, cell, anticipate)
4. FR-MP-004: Stagger MUST support configurable delays
5. FR-MP-005: Stream preset MUST handle token chunking (200ms windows)

**Acceptance Criteria**:
- [ ] All 9 presets defined (mitosis, pulse, drift, lift, compress, drag, morph, stream, interrupt)
- [ ] All presets reference tokens
- [ ] Stagger presets defined (container, item)
- [ ] Presets integrate with Framer Motion
- [ ] Reduced motion respected (no forced animations)

---

## 3. API Contracts

### 3.1 REST Endpoints

**Note**: C008 is a frontend UI change with no new REST endpoints. Widget delivery uses LangGraph server-driven UI (C007).

### 3.2 WebSocket Channels

**Note**: Voice WebSocket is defined in C004 voice-streaming. C008 consumes existing WebSocket for widget spawning.

### 3.3 Port Assignments

**Note**: No new ports for C008. Uses existing frontend port from C007 (3000).

---

## 4. Data Model Mappings

### 4.1 Pydantic → Zod Mappings

**Note**: C008 is frontend-only with no backend DTOs. Widget protocol uses TypeScript types defined in C007.

### 4.2 Shared Types

**Widget Message Protocol** (from C007 frontend-architecture):

```typescript
// Frontend (TypeScript) - Server-driven UI
type WidgetMessage = {
  type: 'widget'
  id: string
  component: WidgetType
  anchor?: AnchorPosition
  size?: 'micro' | 'small' | 'medium' | 'large'
  props: Record<string, any>
}

type WidgetType =
  | 'markdown'
  | 'card'
  | 'form'
  | 'progress'
  | 'action'
  | 'confirmation'
  | 'image'
  | 'gallery'
  | 'chart'
  | 'searchResult'
  | 'hopProgress'
  | 'citationCard'

type AnchorPosition =
  | 'top-left'
  | 'top-center'
  | 'top-right'
  | 'mid-left'
  | 'mid-right'
  | 'bottom-left'
  | 'bottom-right'

// Backend (Python) - LangGraph emits these
push_ui_message(
  "card",  # component name
  {"title": "...", "content": "..."},  # props
  message=message  # LangGraph message
)
```

---

## 5. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| **C007-frontend-architecture** | Prerequisite | Provides LangGraph server-driven UI pattern (`push_ui_message()`, `LoadExternalComponent`) |
| **C003-agent-pipeline** | Prerequisite | Defines LangGraph state management with `ui_message_reducer` |
| **C002-data-contracts** | Reference | Provides Pydantic ↔ Zod alignment patterns (not directly used for frontend-only tokens) |
| **C004-voice-streaming** | Consumer | Voice nucleus consumes voice WebSocket for audio streaming |

---

**Next Artifact**: validate.md
