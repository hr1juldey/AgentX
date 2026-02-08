# Design: Morphing Central Island

Technical design for the morphing UI component with biological metaphors (cell engulfing, cilia typing, metaball merging) that serves as AGENTX's primary generative UI interface.

---

## Context

### Background

AGENTX requires a **minimal-surface generative UI** that transforms based on user intent. Traditional UI paradigms clutter screens with persistent controls. The Morphing Central Island establishes a single anchor point that:

1. **Spawns modes on demand** via longpress gesture
2. **Transforms biologically** using cell engulfing animations
3. **Generates widgets organically** via cell birth metaphor
4. **Uses biological metaphors** throughout (cilia, metaballs, breathing)

### Current State

**Existing Components to Reference:**
- `physics-cells-voice` - Metaball merge, spring physics, energy accumulation
- `R014_ui_showcase` - Force layout, widget types, WebSocket communication
- `globals.css` - Organic UI C008 color tokens, spacing system

**Design System (from globals.css):**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORGANIC UI C008: COLOR TOKENS                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  NEUTRAL / STRUCTURAL                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ --color-void:        0 0% 4%   → #0A0A0A  (deep black background)  │   │
│  │ --color-membrane:    0 0% 8%   → #141414  (borders, dividers)      │   │
│  │ --color-cell:        0 0% 12%  → #1E1E1E  (card backgrounds)       │   │
│  │ --color-nucleus:     0 0% 100% → #FFFFFF  (primary text)          │   │
│  │ --color-cytoplasm:   0 0% 63%  → #A0A0A0  (secondary text)        │   │
│  │ --color-vacuole:     0 0% 40%  → #666666  (tertiary text, icons)   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ACCENT / FUNCTIONAL                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ --color-enzyme:       187 100% 50% → #00D9FF  (primary action)     │   │
│  │ --color-mitochondria: 17 90% 60%  → #FF6B35  (warm accent)         │   │
│  │ --color-golgi:        50 100% 50% → #FFD700  (highlight)           │   │
│  │ --color-lysosome:     4 90% 63%  → #FF4757  (error, delete)        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  MODE-SPECIFIC COLORS (for mode islands)                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Voice Mode:    --color-endoplasmic: 270 60% 70% → #C792EA (purple)  │   │
│  │ Chat Mode:     --color-actin:       220 70% 73% → #82AAFF (blue)   │   │
│  │ File Mode:     --color-microtubule: 164 100% 67% → #64FFDA (green)  │   │
│  │ Camera Mode:   --color-mitochondria: 17 90% 60% → #FF6B35 (orange) │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  SPACING TOKENS (C008)                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ --spacing-atom:       4px   (minimal gap)                           │   │
│  │ --spacing-molecule:   8px   (tight spacing)                         │   │
│  │ --spacing-organelle:  16px  (comfortable padding)                   │   │
│  │ --spacing-cell:       24px  (section spacing)                       │   │
│  │ --spacing-tissue:     32px  (component spacing)                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Constraints

1. **Performance**: 60 FPS animation with multiple cells, force layout calculations
2. **Component Isolation**: Each subcomponent in separate file to prevent re-renders
3. **Mock Data**: Use mock random widget spawning (no real backend for library demo)
4. **Cross-platform**: Desktop (mouse) + mobile (touch) with haptic feedback

---

## Goals / Non-Goals

### Goals

1. **Minimal Surface UI**: Single nucleus that spawns all interactions on demand
2. **Biological Metaphors**: Cell engulfing, cilia typing, metaball merging throughout
3. **Smooth Animations**: 60 FPS with spring physics, no jank
4. **Component Reusability**: Isolated subcomponents that can be used independently
5. **Library-Ready**: Demo page with controls, live previews, documentation

### Non-Goals

1. **Backend Integration**: Real LangGraph WebSocket (mock for now)
2. **Voice Mode Full Features**: Real STT/TTS (use physics-cells pattern as reference)
3. **Camera/File Full Features**: Full upload pipeline (just UI shell)
4. **Accessibility Full Compliant**: Basic keyboard navigation, not full WCAG

---

## Decisions

### Decision 1: Component Architecture - Isolated Subcomponents

**Choice**: Each major component in separate file with React.lazy() loading.

**Rationale**:
- Prevents useless re-renders when only one mode changes
- Allows independent testing of each component
- Enables code splitting for smaller bundle size
- Fixes R014 issue where all components in one file caused re-renders

**File Structure**:

```
frontend/src/components/central-island/
├── index.ts                          # Main export, lazy loaders
├── nucleus.tsx                       # Central nucleus component
├── mode-islands.tsx                  # Mode selection islands
├── voice-mode/
│   ├── index.ts                      # Voice mode export
│   ├── voice-nucleus.tsx             # Mic toggle nucleus
│   ├── cell-emergence.tsx            # Cell birth animation
│   └── draggable-cell.tsx            # Draggable cell with metaball
├── chat-mode/
│   ├── index.ts                      # Chat mode export
│   ├── chat-bar-container.tsx        # Bar morph container
│   ├── paper-display.tsx             # Top paper section
│   ├── keyboard-input.tsx            # Bottom input section
│   ├── horizontal-divider.tsx        # Divider with cilia
│   └── cilia/
│       ├── cilia-filament.tsx        # Individual cilium
│       └── hammer-strike.tsx         # Hammer animation wrapper
├── camera-mode/
│   └── index.ts                      # Camera mode shell
├── file-mode/
│   └── index.ts                      # File mode shell
└── progress/
    └── backend-progress-ring.tsx     # Metaball progress indicator
```

**Component Loading Pattern**:

```typescript
// index.ts
export { Nucleus } from './nucleus';
export { ModeIslands } from './mode-islands';

// Lazy-loaded mode components
export const VoiceMode = lazy(() => import('./voice-mode'));
export const ChatMode = lazy(() => import('./chat-mode'));
export const CameraMode = lazy(() => import('./camera-mode'));
export const FileMode = lazy(() => import('./file-mode'));
```

---

### Decision 2: Color System - Mode-Based Accent Colors

**Choice**: Use C008 accent colors for mode identification.

**Color Mapping**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MODE COLOR MAPPING (C008 TOKENS)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  VOICE MODE                                                                 │
│  Primary:   --color-endoplasmic  → #C792EA (purple)                        │
│  Secondary: --color-golgi         → #FFD700 (gold) for mic toggle          │
│  Nucleus:   --color-nucleus       → #FFFFFF (white)                        │
│                                                                             │
│  CHAT MODE                                                                  │
│  Primary:   --color-actin         → #82AAFF (blue)                         │
│  Secondary: --color-enzyme        → #00D9FF (cyan) for cilia               │
│  Paper:     --color-cell          → #1E1E1E (dark)                         │
│  Divider:   --color-membrane      → #141414 (border)                       │
│                                                                             │
│  FILE MODE                                                                  │
│  Primary:   --color-microtubule  → #64FFDA (green)                         │
│  Secondary: --color-enzyme        → #00D9FF (cyan) for drag zone           │
│                                                                             │
│  CAMERA MODE                                                                │
│  Primary:   --color-mitochondria → #FF6B35 (orange)                        │
│  Secondary: --color-lysosome      → #FF4757 (red) for recording indicator  │
│                                                                             │
│  PROGRESS RING                                                              │
│  Base:      --color-enzyme        → #00D9FF (cyan)                         │
│  Accent:    --color-nucleus       → #FFFFFF (white) for arc/circles        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**CSS Variables Usage**:

```css
/* Mode-specific color classes */
.mode-voice { --mode-primary: hsl(var(--color-endoplasmic)); }
.mode-chat { --mode-primary: hsl(var(--color-actin)); }
.mode-file { --mode-primary: hsl(var(--color-microtubule)); }
.mode-camera { --mode-primary: hsl(var(--color-mitochondria)); }
```

---

### Decision 3: State Management - Recoil with Per-Mode Atoms

**Choice**: Use Recoil for global state with per-mode atoms.

**Rationale**:
- Per-mode atoms prevent cross-mode re-renders
- Recoil's selector system optimizes re-render triggers
- Easy to persist mode state to localStorage
- Better than Context for component tree isolation

**State Structure**:

```typescript
// Global atoms
atom nucleusState: 'idle' | 'longpress' | 'mode-selected'
atom activeMode: 'voice' | 'chat' | 'camera' | 'file' | null
atom isLongpressActive: boolean

// Voice mode atoms
atom voiceModeCells: Array<CellWidget>
atom voiceModeIsMicOn: boolean

// Chat mode atoms
atom chatModeInput: string
atom chatModeCilia: Array<CiliumState>
atom chatModeSentMessages: Array<SentMessageCell>

// Progress indicator atom
atom backendProgressState: 'idle' | 'thinking' | 'stt' | 'generating'
```

**Component Subscription Pattern**:

```typescript
// Only voice-mode components subscribe to voiceModeCells
// Only chat-mode components subscribe to chatModeInput
// This prevents cross-mode re-renders
```

---

### Decision 4: Animation System - Framer Motion + Custom Spring

**Choice**: Framer Motion for gestures + custom spring physics for organic motion.

**Rationale**:
- Framer Motion: Built-in drag, tap, hover detection
- Custom spring: Reuse physics-cells spring-damping pattern
- Performance: GPU-accelerated transforms, optimized re-renders

**Spring Configuration (from physics-cells)**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SPRING PHYSICS CONFIGURATION                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  NUCLEUS MORPH (Circle → Bar)                                               │
│  Stiffness: 300  |  Damping: 30  |  Duration: ~150ms                      │
│  Effect: Snappy with slight overshoot                                       │
│                                                                             │
│  MODE ISLAND SPAWN                                                           │
│  Stiffness: 200  |  Damping: 25  |  Duration: ~200ms                      │
│  Effect: Smooth emergence from center                                       │
│                                                                             │
│  SEQUENTIAL COLLAPSE                                                         │
│  Stiffness: 400  |  Damping: 20  |  Duration: ~100ms                      │
│  Effect: Quick merge with elastic bounce                                    │
│                                                                             │
│  CELL EMERGENCE                                                              │
│  Stiffness: 150  |  Damping: 20  |  Duration: ~400ms                      │
│  Effect: Slow, organic birth motion                                         │
│                                                                             │
│  CILIA HAMMER STRIKE                                                         │
│  Stiffness: 400  |  Damping: 20  |  Duration: ~150ms (100ms up, 50ms settle)│
│  Effect: Snappy "cchunk" with bounce                                        │
│                                                                             │
│  PROGRESS RING ROTATION                                                      │
│  Linear easing, 8000ms infinite repeat                                      │
│  Effect: Smooth, hypnotic rotation                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Animation Timing (Sequence for Chat Mode)**:

```
FRAME 0ms:   Nucleus circle (60px diameter)
FRAME 150ms: Ellipse stretch begins
FRAME 300ms: Full bar formed (400px × 50px)
FRAME 450ms: Paper section expands upward
FRAME 500ms: Cilia emerge from divider (hidden until typing)
```

---

### Decision 5: Click vs Drag Detection - Distance Threshold Fix

**Choice**: Track dragDistance from onMouseDown to onMouseUp with 5px threshold.

**Rationale**:
- Fixes R014 bug where onClick fired after drag
- 5px threshold accommodates mouse jitter
- Explicit state tracking prevents ambiguity

**Implementation Pattern**:

```typescript
const [dragDistance, setDragDistance] = useState(0);
const dragStartPosition = useRef({ x: 0, y: 0 });

const handleMouseDown = (e: MouseEvent) => {
  dragStartPosition.current = { x: e.clientX, y: e.clientY };
  setDragDistance(0);
};

const handleMouseMove = (e: MouseEvent) => {
  const dx = e.clientX - dragStartPosition.current.x;
  const dy = e.clientY - dragStartPosition.current.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  setDragDistance(distance);
};

const handleMouseUp = () => {
  if (dragDistance < 5) {
    // This was a CLICK
    onClick();
  } else {
    // This was a DRAG
    onDragEnd();
  }
  setDragDistance(0);
};
```

---

### Decision 6: Metaball Filter - Reuse from physics-cells

**Choice**: Reuse SVG metaball filter from physics-cells-voice component.

**Rationale**:
- Proven implementation with correct blur/threshold values
- Single filter on parent group (performance)
- Easy to parameterize for different cell sizes

**Filter Configuration**:

```xml
<svg style={{ position: 'absolute', width: 0, height: 0 }}>
  <defs>
    <filter id="metaball-central-island">
      <!-- Gaussian blur for soft edges -->
      <feGaussianBlur
        in="SourceGraphic"
        stdDeviation="16"
        result="blur"
      />
      <!-- Color matrix for alpha thresholding -->
      <feColorMatrix
        in="blur"
        mode="matrix"
        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -7"
        result="goo"
      />
      <!-- Composite for clean edges -->
      <feComposite
        in="SourceGraphic"
        in2="goo"
        operator="atop"
      />
    </filter>
  </defs>
</svg>
```

**Application**:

```typescript
<motion.div
  style={{ filter: 'url(#metaball-central-island)' }}
  className="metaball-container"
>
  <Nucleus />
  <ModeIslands />
  {activeMode === 'voice' && <VoiceCells />}
</motion.div>
```

---

### Decision 7: Force Layout - D3-Force Simulation

**Choice**: Use d3-force for circle positioning with dynamic radius.

**Rationale**:
- Proven pattern from R014 ForceGraphLayout
- Automatic collision detection prevents overlap
- Dynamic radius scales with cell count

**Force Configuration**:

```typescript
const forces = {
  radial: forceRadial(radius, center.x, center.y).strength(0.8),
  charge: forceManyBody().strength(-50),
  collide: forceCollide((d) => d.radius + 8).iterations(2),
  center: forceCenter(center.x, center.y).strength(0.1),
};

const getRadius = (count: number): number => {
  if (count <= 4) return 160;
  if (count <= 8) return 200;
  return 240;
};
```

**Cell Positioning**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FORCE LAYOUT CIRCLE POSITIONING                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1-4 CELLS:     Radius 160px                                                │
│                                                                             │
│           ╭────╮                                                            │
│       ╭──╯    ╰──╮                                                          │
│     ╭─╯      ◉      ╰─╮  ◉ = nucleus                                      │
│     │     nucleus     │  ╭────╯ = cell                                     │
│     ╰─╮            ╭──╯                                                      │
│       ╰──╮  ╭─────╯                                                         │
│           ╰────╯                                                            │
│                                                                             │
│  5-8 CELLS:     Radius 200px                                                │
│                                                                             │
│         ╭────╮                                                              │
│     ╭───╯ ╭──╯ ╰───╮                                                        │
│   ╭─╯     ◉       ╰─╮                                                      │
│  │  ╭──────╮──────╮  │                                                     │
│  │  │      │      │  │                                                     │
│  ╰─╯ ╰─────╯─────╯ ╰─╯                                                     │
│                                                                             │
│  9-12 CELLS:    Radius 240px                                                │
│                                                                             │
│       ╭────────╮                                                           │
│    ╭──╯ ╭──╯ ╰──╮ ╰──╮                                                      │
│  ╭─╯    ◉         ╰───╮                                                    │
│  │  ╭────────╮      ╰─╮                                                   │
│  │  │        │        │                                                   │
│  ╰─╯ ╰───────╯───────╯ │                                                   │
│       ╰─────────────╯ ╰─╁                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Decision 8: Longpress Detection - Custom Hook with Haptic

**Choice**: Custom useLongpress hook with 1.5s duration + haptic at 1.0s.

**Rationale**:
- Consistent timing across all interactions
- Haptic feedback improves mobile UX
- Cancel on move away prevents accidental triggers

**Hook Interface**:

```typescript
interface UseLongpressOptions {
  duration?: number;        // Default: 1500ms
  onCancel?: () => void;     // Called when user moves away
  onHaptic?: () => void;     // Called at 1000ms
}

interface UseLongpressReturn {
  isLongpressActive: boolean;
  longpressProgress: number; // 0 to 1
  bind: {
    onMouseDown: () => void;
    onMouseUp: () => void;
    onMouseLeave: () => void;
    onTouchStart: () => void;
    onTouchEnd: () => void;
  };
}
```

**Animation States**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LONGPRESS TIMELINE (1500ms total)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  IDLE (0ms)                                                                 │
│  ┌──────────┐                                                               │
│  │    ◉     │  Nucleus: 60px circle, subtle pulse                          │
│  │  Hold    │  Pulse: 1.0 → 1.05 scale, 3s duration                        │
│  └──────────┘                                                               │
│                                                                             │
│  LONGPRESS START (0-1000ms)                                                 │
│  ┌──────────┐                                                               │
│  │    ◉     │  Pulse accelerates: 3s → 1s duration                        │
│  │  ....    │  NO progress ring (that's for backend only)                 │
│  └──────────┘                                                               │
│                                                                             │
│  HAPTIC FEEDBACK (1000ms)                                                   │
│  ┌──────────┐                                                               │
│  │    ◉     │  navigator.vibrate(200) - mobile only                       │
│  │  ....    │  Visual fallback: pulse gets faster (1s → 0.5s)             │
│  └──────────┘                                                               │
│                                                                             │
│  TRIGGER APPROACHING (1000-1500ms)                                          │
│  ┌──────────┐                                                               │
│  │    ◉     │  Pulse: 0.5s duration, scale 1.0 → 1.15                     │
│  │  ....    │  Prepares for "graceful spill apart"                        │
│  └──────────┘                                                               │
│                                                                             │
│  GRACEFUL SPILL APART (1500ms)                                              │
│         Voice                                                                │
│      Chat   File                                                             │
│         Camera                                                               │
│    All 4 islands emerge from nucleus in cardinal directions                 │
│                                                                             │
│  CANCEL BEHAVIOR                                                            │
│  - Move away > 50px during longpress → cancel                               │
│  - Click arbitrary free space → cancel                                      │
│  - Release before 1500ms → cancel                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Decision 9: Chat Bar Structure - Two-Phase Morph

**Choice**: Circle → bar (Phase 1), then paper expands upward (Phase 2).

**Rationale**:
- Separates concerns: morph first, then expand paper
- Paper only appears when needed (after chat mode selected)
- Allows cilia to emerge from divider cleanly

**Phase 1: Circle → Bar Morph**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: CIRCLE → BAR MORPH                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FRAME 0ms (Nucleus State)                                                 │
│  ┌──────────┐                                                               │
│  │    ◉     │  Circle: 60px diameter                                      │
│  │  Chat    │  Color: --color-actin (blue #82AAFF)                        │
│  └──────────┘  Position: Center screen                                     │
│                                                                             │
│  FRAME 150ms (Stretch Begins)                                              │
│  ⬭                                                                         │
│  Ellipse: width 60 → 200, height 60 → 55                                   │
│                                                                             │
│  FRAME 300ms (Full Bar Formed)                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                │
│  Full bar: 400px × 50px, border-radius 25px                                │
│  Color: --color-actin background, --color-nucleus text                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Phase 2: Paper Expansion**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 2: PAPER EXPANSION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FRAME 450ms (Paper Emerges)                                               │
│  ┌──────────────────────────────────────────────────────────┐              │
│  │                                                          │  ← Paper     │
│  │                                                          │    (empty)   │
│  ├──────────────────────────────────────────────────────────┤  ← Divider   │
│  │ Type or speak your message...         [Send]             │  ← Keyboard  │
│  └──────────────────────────────────────────────────────────┘              │
│       Paper height: 0 → 100px (animated)                                  │
│       Divider: 1px, --color-membrane (#141414)                             │
│       Keyboard: Stable 50px height                                          │
│                                                                             │
│  FRAME 500ms (Cilia Emerge from Divider)                                   │
│  ┌──────────────────────────────────────────────────────────┐              │
│  │                                                          │              │
│  ├──────────────────────────────────────────────────────────┤  ← Divider   │
│  │  │  │  │  │                                               │  ← Cilia    │
│  │  ╱  ╱  ╱  ╱                                               │    (hidden   │
│  │ Type or speak your message...         [Send]             │     until     │
│  └──────────────────────────────────────────────────────────┘      typing)  │
│                                                                             │
│  USER TYPES "h"                                                             │
│  ┌──────────────────────────────────────────────────────────┐              │
│  │ h                                                        │  ← "h" in   │
│  ├──────────────────────────────────────────────────────────┤  ← paper     │
│  │  │                                                        │              │
│  │  ╱  Cilium #1 extends UPWARD with hammer animation        │              │
│  │ Type or speak your message...         [Send]             │              │
│  └──────────────────────────────────────────────────────────┘              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Component Structure**:

```typescript
<div className="chat-bar-container">
  {/* Phase 2: Paper section (expands upward) */}
  <AnimatePresence>
    {barPhase >= 'paper-expanded' && (
      <motion.div
        initial={{ height: 0, opacity: 0 }}
        animate={{ height: 'auto', opacity: 1 }}
        className="paper-display"
        style={{
          background: 'hsl(var(--color-cell))', // #1E1E1E
          borderTop: `1px solid hsl(var(--color-membrane))`,
        }}
      >
        {cilia.map((c) => (
          <CiliumFilament key={c.id} {...c} />
        ))}
        <div className="paper-content">{currentInput}</div>
      </motion.div>
    )}
  </AnimatePresence>

  {/* Divider that holds cilia */}
  <div
    className="horizontal-divider"
    style={{
      background: 'hsl(var(--color-membrane))', // #141414
      height: '1px',
    }}
  />

  {/* Phase 1: Keyboard input (stable) */}
  <div className="keyboard-input">
    <input
      type="text"
      value={currentInput}
      onChange={(e) => setCurrentInput(e.target.value)}
      placeholder="Type or speak your message..."
      style={{
        background: 'hsl(var(--color-membrane))', // #141414
        color: 'hsl(var(--color-nucleus))', // #FFFFFF
      }}
    />
    <button className="send-button">Send</button>
  </div>
</div>
```

---

### Decision 10: Progress Ring - Metaball Orbiting Animation

**Choice**: Ported from Kotlin ProgressLoader with metaball effect.

**Rationale**:
- Proven visual pattern from metaballs library
- Hypnotic rotation indicates "agent is thinking"
- Metaball merge creates organic, living feel

**Visual Structure**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BACKEND PROGRESS RING (Kotlin Port)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CENTER OF NUCLEUS (when backend processing)                                │
│                                                                             │
│         ╭────────────────────────────────────────────────╮                 │
│       ╱                                                   ╲               │
│      │  ┌────────────────────────────────────────────┐    │               │
│      │  │     ╭────╮  ╭────╮  ╭────╮  ╭────╮      │    │               │
│      │  │     │    ╱  ╱    │  ╱    │  ╱    │      │    │               │
│      │  │     │   ╱  ╱     │ ╱     │╱      │      │    │               │
│      │  │     │  ╱  ╱  ────╯╱─────╯╱────── │      │    │               │
│      │  │     │ ╱  ╱         │     ╱       │      │    │               │
│      │  │     │╱  ╱          │    ╱        │      │    │               │
│      │  │     ╯╱  ╱    ╭─────╯   ╱         ╯      │    │               │
│      │  │      ╲  ╱    ╱         ╱                │    │               │
│      │  │       ╲╱────╯─────────╯                 │    │               │
│      │  │        ◯                                 │    │               │
│      │  │    (rotating arc)                         │    │               │
│      │  └────────────────────────────────────────────┘    │               │
│      │                                                    │               │
│       ╲                                                   ╱               │
│         ╰────────────────────────────────────────────────╯                 │
│                                                                             │
│  ALL WRAPPED IN METABALL FILTER (blur radius: 40px)                         │
│                                                                             │
│  COMPONENTS:                                                                │
│  1. Rotating Arc (215° sweep)                                               │
│     - Rotation: 0° → -360° (clockwise), 8000ms, linear, infinite           │
│     - Stroke width: 19.5% of size                                          │
│     - Color: --color-nucleus (#FFFFFF)                                     │
│                                                                             │
│  2. Orbiting Circles (9 × 50px circles)                                    │
│     - Orbit: 0° → 360° (counterclockwise), 8000ms, linear, infinite        │
│     - Offset: Each circle 40° apart (360° / 9)                             │
│     - Color: --color-nucleus (#FFFFFF)                                     │
│                                                                             │
│  3. Metaball Container                                                      │
│     - Base color: --color-enzyme (#00D9FF - cyan)                          │
│     - Blur radius: 40px                                                    │
│                                                                             │
│  WHEN TO SHOW:                                                              │
│  - Backend agents processing (LangGraph thinking)                           │
│  - Audio being sent to STT                                                  │
│  - Widget being generated/hydrated                                         │
│  - HIDDEN: During longpress, idle state, local UI transitions              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Animation Code**:

```typescript
const { rotate: arcRotate } = useAnimate(
  () => arcRotate.set(0),
  { rotate: -360 },
  {
    duration: 8000,
    ease: 'linear',
    repeat: Infinity,
  }
);

const { rotate: circleRotate } = useAnimate(
  () => circleRotate.set(0),
  { rotate: 360 },
  {
    duration: 8000,
    ease: 'linear',
    repeat: Infinity,
  }
);

// 9 circles, each offset by 40°
{[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
  <Circle
    key={i}
    offset={i * (360 / 9)} // 40° intervals
    rotation={circleRotate}
  />
))}
```

---

## Component Architecture (ASCII Diagrams)

### Full Component Tree

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MORPHING CENTRAL ISLAND: COMPONENT TREE                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  <CentralIsland> (index.ts)                                                │
│  │                                                                          │
│  ├─ <Nucleus> (nucleus.tsx)                                                │
│  │   ├─ Idle state: 60px circle with pulse                                 │
│  │   ├─ Longpress state: Accelerating pulse                                │
│  │   ├─ Progress ring: Backend processing (optional)                       │
│  │   └─ Mic toggle: Voice mode active                                     │
│  │                                                                          │
│  ├─ <ModeIslands> (mode-islands.tsx)                                       │
│  │   ├─ VoiceIsland (top, purple #C792EA)                                  │
│  │   ├─ ChatIsland (left, blue #82AAFF)                                    │
│  │   ├─ FileIsland (right, green #64FFDA)                                  │
│  │   └─ CameraIsland (bottom, orange #FF6B35)                             │
│  │                                                                          │
│  ├─ <VoiceMode> (voice-mode/index.ts) - LAZY LOADED                        │
│  │   ├─ <VoiceNucleus> - Mic toggle in center                              │
│  │   ├─ <CellEmergence> - Cell birth animation                             │
│  │   ├─ <DraggableCell>[] - Auto-positioned, draggable widgets              │
│  │   └─ <ForceLayout> - D3-force simulation                                │
│  │                                                                          │
│  ├─ <ChatMode> (chat-mode/index.ts) - LAZY LOADED                          │
│  │   ├─ <ChatBarContainer> - Morph animation wrapper                        │
│  │   │   ├─ <PaperDisplay> - Top section, shows input                      │
│  │   │   │   └─ <CiliumFilament>[] - Hair texture, hammer animation        │
│  │   │   ├─ <HorizontalDivider> - Holds cilia, separates sections          │
│  │   │   └─ <KeyboardInput> - Bottom input, stable                         │
│  │   └─ <SentMessageCell>[] - Floating cells from sent messages            │
│  │                                                                          │
│  ├─ <CameraMode> (camera-mode/index.ts) - LAZY LOADED                      │
│  │   └─ getUserMedia shell (implementation placeholder)                    │
│  │                                                                          │
│  ├─ <FileMode> (file-mode/index.ts) - LAZY LOADED                          │
│  │   └─ Drag-drop zone shell (implementation placeholder)                   │
│  │                                                                          │
│  └─ <BackendProgressRing> (progress/backend-progress-ring.tsx)             │
│      ├─ Rotating arc (215° sweep, 8s rotation)                             │
│      ├─ 9 orbiting circles (40° offset each)                               │
│      └─ Metaball container (blur 40px)                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### State Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STATE FLOW: INTERACTION SEQUENCES                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  IDLE → LONGPRESS → MODE_SELECTION → MODE_ACTIVE                           │
│                                                                             │
│  ┌──────────┐    1.5s     ┌────────────┐   click   ┌────────────┐         │
│  │          │ ──────────▶ │            │ ─────────▶ │            │         │
│  │   IDLE   │             │ LONGPRESS  │           │ MODE_SELECT │         │
│  │          │ ◀────────── │            │  cancel   │            │         │
│  └──────────┘   move      └────────────┘           └─────┬──────┘         │
│     away                                                                │         │
│                                                                         │         │
│  MODE_SELECT → SEQUENTIAL_COLLAPSE → NUCLEUS_ACTIVE                     │         │
│                                                                         │         │
│  ┌────────────┐   select Voice   ┌──────────────────┐                 │         │
│  │ MODE_SELECT│ ───────────────▶ │ SEQUENTIAL       │                 │         │
│  │            │                 │ COLLAPSE         │                 │         │
│  │ 4 islands  │                 │ Chat→Voice       │                 │         │
│  │ visible    │                 │ File→Voice       │                 │         │
│  └────────────┘                 │ Camera→Voice     │                 │         │
│                                 └────────┬─────────┘                 │         │
│                                          │                            │         │
│                                          ▼                            │         │
│                                 ┌─────────────────┐                   │         │
│                                 │ NUCLEUS_ACTIVE  │ ◀─────────────────┘         │
│                                 │ (single island) │ dismiss mode              │
│                                 └────────┬─────────┘                           │
│                                          │                                      │
│                              ┌───────────┴───────────┐                         │
│                              ▼                       ▼                         │
│                       ┌─────────────┐         ┌─────────────┐                   │
│                       │ Voice Mode  │         │ Chat Mode   │                   │
│                       │ (mic toggle)│         │ (bar morph) │                   │
│                       └─────────────┘         └─────────────┘                   │
│                                                                             │
│  VOICE MODE: CELL EMERGENCE                                                 │
│                                                                             │
│  ┌─────────────┐   backend/mock   ┌─────────────┐   arrive &   ┌──────────┐  │
│  │ NUCLEUS     │ ───────────────▶ │ CELL BIRTH  │ ───────────▶ │ DRAGGABLE│  │
│  │ ACTIVE      │   spawn widget   │             │   bounce    │  CELL    │  │
│  └─────────────┘                  └─────────────┘              └────┬─────┘  │
│                                                                        │        │
│                                                                        ▼        │
│  ┌─────────────┐   drag to center  ┌─────────────┐   absorb &   ┌──────────┐  │
│  │ DRAGGABLE   │ ◀──────────────── │ CELL MERGE  │ ───────────▶ │ NUCLEUS  │  │
│  │ CELL        │   dismiss gesture │             │   elastic   │  ACTIVE  │  │
│  └─────────────┘                  └─────────────┘   bounce     └──────────┘  │
│                                                                             │
│  CHAT MODE: CILIA TYPING                                                    │
│                                                                             │
│  ┌─────────────┐   user types     ┌─────────────┐   send &     ┌──────────┐  │
│  │ KEYBOARD    │ ───────────────▶ │ CILIA       │ ───────────▶ │ FLOATING │  │
│  │ INPUT       │   per keystroke  │ EXTENSION   │   bubble up │  CELL    │  │
│  └─────────────┘                  └─────────────┘              └────┬─────┘  │
│                                                                        │        │
│                                                                        ▼        │
│  ┌─────────────┐   backspace       ┌─────────────┐   retract    ┌──────────┐  │
│  │ CILIA       │ ◀──────────────── │ CILIA       │ ───────────▶ │ KEYBOARD │  │
│  │ EXTENDED    │   reverse anim    │ RETRACT     │             │  INPUT   │  │
│  └─────────────┘                  └─────────────┘              └──────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Risks / Trade-offs

### Risk 1: Performance with Multiple Cells

**Risk**: 60 FPS with 10+ cells, metaball filter, force layout may drop frames.

**Mitigation**:
- Memoize force layout positions (only recalculate on count change)
- Single SVG filter on parent group (not per-cell)
- Use CSS transforms (GPU accelerated)
- requestAnimationFrame loop from physics-cells pattern

### Risk 2: Click vs Drag Detection False Positives

**Risk**: 5px threshold may be too sensitive for mouse jitter.

**Mitigation**:
- Add 50ms debounce to mouse movement
- Track movement delta, not just final distance
- Fallback to onClick if drag never started

### Risk 3: Cross-Mode Re-renders

**Risk**: State changes in one mode trigger re-renders in all modes.

**Mitigation**:
- Recoil atoms with per-mode selectors
- React.lazy() + Suspense for mode components
- Separate state atoms per mode (voiceModeCells, chatModeInput, etc.)

### Risk 4: Metaball Filter Clipping

**Risk**: SVG filter may clip cells near viewport edge.

**Mitigation**:
- Calculate viewBox with padding = blur radius × 3
- Dynamic viewBox sizing based on max cell distance
- Filter ID namespacing for multiple instances

### Risk 5: Longpress Cancel Detection

**Risk**: User moves mouse slightly during longpress, accidentally cancels.

**Mitigation**:
- 50px threshold before cancel (not immediate)
- Visual feedback when threshold approached
- Click free space only cancels after longpress starts

---

## Migration Plan

### Phase 1: Core Infrastructure (Week 1)

1. Create component file structure with isolated subcomponents
2. Set up Recoil atoms for global state
3. Implement metaball filter (reuse from physics-cells)
4. Create useLongpress hook with haptic feedback

### Phase 2: Mode Selection (Week 2)

1. Implement nucleus with longpress detection
2. Create 4 mode islands with cardinal positioning
3. Implement sequential collapse animation
4. Add nucleus morph (circle → bar for chat)

### Phase 3: Voice Mode (Week 3)

1. Implement voice nucleus with mic toggle
2. Create cell emergence animation with mock spawning
3. Add force layout for circle positioning
4. Implement draggable cells with click vs drag fix
5. Add drag-to-center dismiss gesture

### Phase 4: Chat Mode (Week 4)

1. Implement chat bar morph (two-phase)
2. Create horizontal divider component
3. Implement cilia filament with hair texture
4. Add hammer-strike animation per keystroke
5. Implement sent message → floating cell transition

### Phase 5: Polish & Integration (Week 5)

1. Add backend progress ring (Kotlin port)
2. Create demo page with controls
3. Add library routing and card
4. Performance optimization (memoization, lazy loading)
5. Testing (cross-browser, mobile, accessibility)

---

## Open Questions

### Q1: Backend WebSocket Protocol

**Question**: What is the exact message format for widget spawning?

**Options**:
- A: Reuse R014 WebSocketWidgetData format
- B: Create new UIDescriptor format for generative UI
- C: Hybrid: R014 format + new generative fields

**Recommendation**: Option C (Hybrid) - reuse proven R014 pattern, extend with generative fields.

### Q2: Cilia Hair Texture Implementation

**Question**: How to render hair texture on cilia filaments?

**Options**:
- A: SVG filter (turbulence + displacement)
- B: CSS background pattern (repeating linear gradient)
- C: Canvas drawing with procedural hair
- D: CSS mask-image with hair SVG

**Recommendation**: Option B (CSS pattern) for performance, fallback to D for mobile.

### Q3: Force Layout on Mobile

**Question**: Should circle radius scale down on mobile?

**Options**:
- A: Fixed radius (160px) on all devices
- B: Scale radius by viewport width (30vw)
- C: Adaptive breakpoints (160px desktop, 120px mobile)

**Recommendation**: Option C (Adaptive) - prevents cells from being too small on mobile.

### Q4: Sent Message Cell Behavior

**Question**: Should sent messages remain as cells or disappear?

**Options**:
- A: Remain as draggable cells forever
- B: Auto-dismiss after N seconds
- C: Collapse to nucleus when chat mode exits
- D: User choice (toggle in settings)

**Recommendation**: Option A (Remain) - matches vision of "floating around", user can dismiss manually.

---

## Appendix: CSS Variable Reference

### Complete Color Token Mapping

```css
/* NUCLEUS (all modes) */
--nucleus-bg: hsl(var(--color-nucleus));        /* #FFFFFF - white */
--nucleus-text: hsl(var(--color-void));         /* #0A0A0A - black for contrast */

/* VOICE MODE */
--voice-primary: hsl(var(--color-endoplasmic));  /* #C792EA - purple */
--voice-secondary: hsl(var(--color-golgi));     /* #FFD700 - gold */
--voice-cell-bg: hsl(var(--color-cell));         /* #1E1E1E - dark */

/* CHAT MODE */
--chat-primary: hsl(var(--color-actin));         /* #82AAFF - blue */
--chat-secondary: hsl(var(--color-enzyme));      /* #00D9FF - cyan */
--chat-paper: hsl(var(--color-cell));            /* #1E1E1E - dark */
--chat-divider: hsl(var(--color-membrane));      /* #141414 - border */
--chat-keyboard: hsl(var(--color-membrane));     /* #141414 - input bg */

/* FILE MODE */
--file-primary: hsl(var(--color-microtubule));   /* #64FFDA - green */
--file-secondary: hsl(var(--color-enzyme));      /* #00D9FF - cyan */

/* CAMERA MODE */
--camera-primary: hsl(var(--color-mitochondria)); /* #FF6B35 - orange */
--camera-secondary: hsl(var(--color-lysosome));   /* #FF4757 - red (recording) */

/* PROGRESS RING */
--progress-base: hsl(var(--color-enzyme));       /* #00D9FF - cyan */
--progress-accent: hsl(var(--color-nucleus));    /* #FFFFFF - white */

/* SPACING */
--gap-tight: var(--spacing-atom);      /* 4px */
--gap-normal: var(--spacing-molecule); /* 8px */
--gap-loose: var(--spacing-organelle); /* 16px */
--padding-cell: var(--spacing-cell);   /* 24px */

/* BORDER RADIUS */
--radius-sm: var(--radius);            /* 0.5rem = 8px */
--radius-md: calc(var(--radius) * 2);  /* 1rem = 16px */
--radius-lg: calc(var(--radius) * 3);  /* 1.5rem = 24px */
--radius-full: 9999px;                 /* pill shape */

/* ANIMATION DURATION */
--duration-fast: var(--duration-fast);     /* 150ms */
--duration-normal: var(--duration-normal); /* 300ms */
--duration-slow: var(--duration-slow);     /* 500ms */
```

### Tailwind Class Combinations

```css
/* Mode-specific background colors */
.bg-voice { background-color: hsl(var(--color-endoplasmic)); }
.bg-chat { background-color: hsl(var(--color-actin)); }
.bg-file { background-color: hsl(var(--color-microtubule)); }
.bg-camera { background-color: hsl(var(--color-mitochondria)); }

/* Metaball container */
.metaball-group {
  filter: url(#metaball-central-island);
}

/* Nucleus pulse animation */
@keyframes nucleus-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.animate-nucleus-pulse {
  animation: nucleus-pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Longpress pulse (accelerating) */
@keyframes longpress-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.animate-longpress-pulse {
  animation: longpress-pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

---

**End of Design Document**

Next: Create 13 granular specs with LOOKS/WORKS/LAYOUT structure, then tasks.md with frontend-design skill invocations.
