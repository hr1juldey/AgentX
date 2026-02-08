# Proposal: Morphing Central Island

A morphing UI component with biological metaphors (cell engulfing, cilia typing) that serves as a minimal surface for generative UI - a single anchor that transforms based on interaction mode.

## Why

Current UI paradigms clutter the screen with persistent controls. AGENTX needs a **true generative UI** with minimal surface area - a single central nucleus that:

1. **Spawns modes on demand** via longpress (not persistent UI elements)
2. **Transforms biologically** between modes (sequential cell engulfing, not abrupt transitions)
3. **Generates widgets organically** (cells emerging from nucleus, not static modals)
4. **Uses biological metaphors** throughout (cilia typing, metaball merging, breathing animations)

This change establishes the **Central Island** as the primary interaction pattern for AGENTX, replacing traditional navigation and chat interfaces with an organic, morphing UI that responds to user intent through gesture and mode selection.

## What Changes

### New Component: Central Island (Morphing Nucleus)

- **Idle State**: Single circular nucleus (60px) with subtle pulse animation
- **Longpress Trigger (1.5s)**: Nucleus pulse accelerates → "graceful spill apart" → 4 mode islands emerge (Voice, Chat, Camera, File) in cardinal directions
- **Haptic Feedback**: Vibrate at 1.0s during longpress (mobile)
- **Cancel Behavior**: Move away during longpress OR click arbitrary free space
- **NOTE**: Progress ring is NOT for longpress - it's a separate spec for backend agent processing only

### Mode 1: Voice Mode

- **Sequential Collapse**: When Voice selected → Chat, File, Camera islands sequentially slide toward Voice and merge via metaball animation
- **Nucleus Transformation**: Voice nucleus becomes slightly larger, pulses once, mic icon appears in center (toggle on/off)
- **Cell Widget Emergence**:
  - **FOR NOW (Library Demo)**: Mock random widget spawning every 3-5 seconds for visualization
  - **LATER (Production)**: Backend sends widget via LangGraph → nucleus pulses (prepare to birth)
  - Small bud appears on edge (metaball forms)
  - Cell separates, travels outward ~200px (30% screen width, spring trajectory)
  - Cell arrives, bounces once, fully expanded with sticky edges
- **Cell Behavior**:
  - Auto-position in circle around nucleus (force layout)
  - Draggable anywhere after emergence
  - Sticky edges (metaball merge when close to other cells)
- **Dismiss Gesture**: Drag cell toward nucleus → distance < 150px → nucleus pulses → metaball merge → cell shrinks (scale 1 → 0.5 → 0) → nucleus absorbs (elastic bounce)
- **Constraints**: Drag AWAY from nucleus → cell stays; Swipe-away → NO (must return to nucleus); Click-collapse button → NO

### Mode 2: Chat Mode (Biological Typewriter)

- **Sequential Collapse**: Same pattern - other islands merge into Chat island
- **Nucleus Morph to Bar** (Phase 1):
  - Frame 0: Circle nucleus (60px)
  - Frame 150: Stretch horizontally (width 60 → 400, height 60 → 50)
  - Frame 300: Full bar with rounded corners, NO paper yet
- **Paper Emergence** (Phase 2):
  - Frame 450: Top "paper" section expands upward from bar
  - Cilia emerge from TOP edge of paper section (but only extend when typing)
  - Paper is initially empty/hidden until user types
- **Chat Bar Structure**:
  - Top section: "Paper" display (shows current input only, not full history)
  - Bottom section: "Keyboard" input (stable, never moves, constrained ~400px max width)
  - Horizontal divider: Separates sections AND HOLDS THE CILIA (cilia extend from this line)
- **Cilia Transfer Mechanism**:
  - Cilia ONLY extend when typing (not idle)
  - Each keystroke → cilium extends UPWARD with hammer animation (cchunk + bounce)
  - Hair texture filaments (not smooth lines)
  - Sequential hammer strikes (one per character)
- **Backspace Behavior**: Cilia retract with reverse animation (rewind effect, hair shrinks downward)
- **Sent Message**: Paper clears → message bubbles up and floats around → becomes floating cell (auto-positions in circle, draggable, dismissible)

### Mode 3: Camera Mode

- **Sequential Collapse**: Same pattern
- **Nucleus Transformation**: Camera island becomes nucleus with camera icon
- **Widget Behavior**: getUserMedia integration, spawns cells like Voice mode

### Mode 4: File Mode

- **Sequential Collapse**: Same pattern
- **Nucleus Transformation**: File island becomes nucleus with file icon
- **Widget Behavior**: Drag-drop upload zone, spawns cells like Voice mode

### Reused Patterns from Existing Components

**Implementation Reuse from physics-based-cell-division-voice:**

The following specs are FULLY REUSED in morphing-central-island (code copied, not reimplemented):

1. **`metaball-merge-behavior`** → Reused for:
   - Sequential collapse metaball merge
   - Cell sticky edges metaball effect
   - Cell dismiss metaball merge
   - Implementation: Copy from `frontend/src/lib/physics/metaball-filter.tsx`

2. **`physics-spring-damping`** → Reused for:
   - Spring physics API (stiffness/damping configuration)
   - Velocity accumulation and damping
   - Position integration
   - Implementation: Copy from `frontend/src/lib/physics/spring-damping.ts`

3. **`audio-reactive-rendering`** → Reused for:
   - 60 FPS requestAnimationFrame loop
   - SVG coordinate system and viewBox sizing
   - Filter application optimization
   - Responsive sizing (desktop/mobile)
   - Implementation: Copy from `frontend/src/lib/physics/physics-renderer.tsx`

**Partial Reuse (adapted for new context):**

4. **`physics-energy-accumulator`** → Adapted as:
   - Mock widget spawning timer (instead of audio energy)
   - Same spring-driven accumulation pattern

5. **`physics-orbit-mechanics`** → Adapted as:
   - Cell positioning from nucleus (not continuous orbit)
   - Spring trajectory calculation (reused)

**Implementation from R014_ui_showcase:**

6. **Force Layout** → Reused for:
   - D3-force simulation for circle positioning
   - Dynamic radius based on cell count
   - Memoization for performance

**Implementation from Component Library:**

7. **Widget Types** → Reused for:
   - ChartWidget, FormWidget, ImageWidget
   - UIDescriptor interfaces
   - WebSocket data structures (for future backend integration)

## Capabilities

### New Capabilities

Each capability becomes a granular spec at `specs/<name>/spec.md` with detailed scenarios covering **How it LOOKS**, **How it WORKS**, and **How it's LAYOUT**.

#### 1. `nucleus-longpress-trigger`
Longpress detection (1.5s) on central nucleus with pulse acceleration (NOT progress ring - that's only for backend processing) and haptic feedback (vibration at 1.0s), culminating in graceful spill apart that spawns 4 mode islands.

**Key behaviors**:
- Idle: 60px circle nucleus with subtle pulse
- 0-1.5s: Pulse accelerates (faster heartbeat, NO progress ring)
- 1.0s: Vibrate (haptic feedback on mobile)
- 1.5s: Graceful spill apart → Voice, Chat, Camera, File emerge in cardinal directions
- Cancel: Move away during longpress OR click arbitrary free space

#### 1.5. `backend-progress-indicator`
Metaball-based progress ring that appears ONLY when backend agents are processing (LangGraph thinking, STT processing, widget generation) or audio is being sent to STT. Displays in the center of the central nucleus with rotating arc and orbiting circles, all wrapped in metaball merge effect.

**Ported from Kotlin**: Based on `ProgressLoader` composable with metaball merge effect.

**Key behaviors**:
- **When to show**:
  - Backend agents processing (LangGraph thinking, generating response)
  - Audio being sent to STT (speech-to-text)
  - Widget being generated/hydrated
  - HIDDEN: During longpress trigger, idle state, or local UI transitions
- **Position**: Center of central nucleus OR center of active mode-specific nucleus
- **Visual structure**:
  - Rotating arc (215° sweep, 19.5% stroke width)
  - 9 small orbiting circles (50px each, evenly distributed)
  - All wrapped in metaball container (blur radius: 40px)
  - Base color: Blue/Cyan accent (change from Kotlin's 0xFF0951E2)
- **Animation timing**:
  - Arc rotation: 0° → -360° (clockwise) over 8 seconds, linear easing, infinite repeat
  - Circle orbit: 0° → 360° (counterclockwise) over 8 seconds, linear easing, infinite repeat
  - Each circle offset by i × (360° / 9) = 40° intervals
- **Disappear**: Instant fade-out when backend response arrives (no slow collapse)

#### 2. `mode-island-spawn`
Cardinal positioning of 4 mode islands (Voice, Chat, Camera, File) with graceful emergence from nucleus, each island with distinct icon and type-based color.

**Key behaviors**:
- Cardinal positions: Voice (top), Chat (left), File (right), Camera (bottom)
- Animate from nucleus center → final position (spring trajectory)
- Type-based colors: Voice (purple), Chat (blue), File (green), Camera (orange)
- Click island → trigger sequential collapse into that mode

#### 3. `sequential-mode-collapse`
Sequential collapse animation where non-selected islands slide toward selected island one by one and merge via metaball effect, simulating biological cell engulfing.

**Key behaviors**:
- User selects Voice → Chat slides toward Voice and merges (metaball)
- Then File slides toward Voice and merges
- Then Camera slides toward Voice and merges
- Each merge: elastic bounce on nucleus after absorption
- Final state: Single nucleus (slightly larger, pulses once)

#### 4. `nucleus-morph-animation`
Morphing animation of nucleus shape based on selected mode: circle stays circular for Voice/Camera/File modes, but stretches horizontally to become chat input bar for Chat mode.

**Key behaviors**:
- Voice/Camera/File modes: Nucleus remains circular, slight scale increase (1.0 → 1.1)
- Chat mode: Circle (60px) → Ellipse stretch → Full bar (400px width, 50px height) with rounded corners (25px border-radius)
- Animation duration: 150ms (stretch), 150ms (bar formation)
- Spring configuration: stiffness 300, damping 30

#### 5. `voice-mode-cell-emergence`
Cell widget emergence animation from voice nucleus with biological birth metaphor (bud → separate → travel → arrive → bounce).

**FOR NOW (Library Demo)**: Mock random widget spawning every 3-5 seconds for visualization
**LATER (Production)**: Backend sends widget via LangGraph WebSocket

**Key behaviors**:
- Timeline:
  - 0ms: Nucleus pulses (prepare to birth)
  - 200ms: Small bud appears on edge (metaball starts forming)
  - 400ms: Cell separates, travels outward ~200px (30% screen width, spring trajectory)
  - 600ms: Cell arrives at destination, bounces once
  - 800ms: Cell fully expanded, sticky edges engaged
- Direction: Auto-position in circle around nucleus (determined by force layout)
- Spring trajectory: Ease-out cubic with slight overshoot

#### 6. `cell-force-layout`
Auto-positioning of multiple cells in circle around nucleus using D3-force simulation, with dynamic radius based on cell count (1-4: 160px, 5-8: 200px, 9-12: 240px).

**Key behaviors**:
- Forces: radial (strength 0.8), charge (-50), collide (radius + 8), center (0.1)
- Run simulation for 300 ticks, memoize positions
- Prevent recursive updates (only recalculate when cell count changes)
- Returns: Record<string, { x, y }> of cell positions

#### 7. `draggable-cells`
Draggable cell widgets with click vs drag detection (distance threshold 5px), sticky edges (metaball merge when close), and viewport bounds checking.

**CRITICAL FIX FROM R014**: R014 had a bug where click vs drag wasn't properly differentiated. This spec MUST fix that bug.

**Key behaviors**:
- Drag: Framer Motion drag with whileDrag={{ scale: 1.05, cursor: "grabbing", zIndex: 50 }}
- Click detection: Track dragDistance from onMouseDown to onMouseUp
  - dragDistance < 5px → CLICK (trigger onClick)
  - dragDistance >= 5px → DRAG (trigger onDragEnd, NOT onClick)
- Sticky edges: When cells get close (< blur threshold), metaball merge activates
- Viewport bounds: Prevent cells from being dragged off-screen

#### 8. `cell-dismiss-gesture`
Drag-to-center dismiss gesture where user drags cell toward nucleus, nucleus pulses when ready to receive, metaball merge begins on contact, cell shrinks and gets absorbed with elastic bounce.

**Key behaviors**:
- Distance < 150px → nucleus pulses (ready to receive)
- Contact → metaball merge begins
- Cell shrinks: scale 1 → 0.5 → 0
- Nucleus absorbs: scale 1 → 1.2 → 1 (elastic bounce)
- Constraints:
  - Drag AWAY from nucleus → cell stays, doesn't escape viewport
  - Swipe-away → NO, must return to nucleus
  - Click-collapse button → NO, drag-to-center only

#### 9. `chat-bar-structure`
Chat input bar structure with TWO-PHASE emergence: Phase 1 (circle → bar), Phase 2 (paper expands upward). Top "paper" display (shows current input only) and bottom "keyboard" input (stable, constrained ~400px max width), separated by horizontal divider.

**Key behaviors**:
- Phase 1: Nucleus morphs from circle (60px) → bar (400px × 50px)
- Phase 2: Paper section expands upward from bar (initially empty/hidden)
- Top section: "Paper" display - shows what's being typed, scrollable, half-contained space
- Bottom section: "Keyboard" input - stable textarea or input field, never moves
- Divider: 1px horizontal line separating sections
- Max width: ~400px (constrained, not full screen)
- Border-radius: 25px (fully rounded corners)

#### 10. `cilia-transfer-mechanism`
Biological typewriter metaphor where cilia (hair-texture filaments) extend upward FROM THE HORIZONTAL DIVIDER to transfer keystrokes to paper section, with sequential hammer-strike motion per character.

**Key behaviors**:
- Cilia ONLY extend when typing (not idle)
- Each keystroke → new cilium extends UPWARD from horizontal divider
- Hair texture: Filament with "hair" detail (not smooth line)
- Sequential: One cilium per character, extending left-to-right
- Transfer metaphor: Cilia visually transfer text from keyboard (below divider) to paper (above divider)
- Position: EXTEND FROM THE HORIZONTAL DIVIDER (not from keyboard section directly)

#### 11. `hammer-strike-animation`
Per-keystroke hammer-strike animation for each cilium extension with "cchunk + bounce" effect - quick scale-up with elastic bounce, simulating typewriter hammer striking paper.

**Key behaviors**:
- Animation: Scale 0 → 1.2 → 1.0 (cchunk + bounce)
- Duration: 150ms total (100ms scale-up, 50ms bounce settle)
- Spring: stiffness 400, damping 20 (snappy with bounce)
- Per keystroke: One hammer animation per character typed
- Backspace: Reverse animation (rewind effect, hair shrinks downward)

#### 12. `sent-message-float`
Sent message transition where paper clears and message bubbles up, becoming floating cell that auto-positions in circle around nucleus, joining other widgets as draggable, dismissible cell.

**Key behaviors**:
- Send triggered → paper section clears (opacity 1 → 0)
- Message bubbles up: translateY(+20px) with ease-out
- Transforms to cell: Morphs into cell widget (border, shadow, metaball-ready)
- Auto-position: Joins force layout circle around nucleus
- Becomes draggable: Can be repositioned like other cells
- Dismissible: Drag-to-center gesture works on sent message cells

### Modified Capabilities

None. This is a new component with no changes to existing specs.

## Impact

### Affected Code

**New Files**:
- `frontend/src/components/central-island/` - Main component directory
  - `nucleus.tsx` - Central nucleus component
  - `mode-islands.tsx` - Mode selection islands
  - `voice-mode.tsx` - Voice mode with cell widgets
  - `chat-mode.tsx` - Chat mode with biological typewriter
  - `camera-mode.tsx` - Camera mode
  - `file-mode.tsx` - File mode
- `frontend/src/components/central-island/cilia/` - Cilia typewriter components
  - `cilia-filament.tsx` - Individual cilium with hair texture
  - `hammer-animation.tsx` - Hammer-strike animation wrapper
  - `paper-display.tsx` - Top paper display section
  - `keyboard-input.tsx` - Bottom keyboard input section
  - `horizontal-divider.tsx` - Divider that holds cilia (NEW)
- `frontend/src/components/central-island/progress/` - Backend progress indicator
  - `backend-progress-ring.tsx` - Metaball progress ring (ported from Kotlin)
- `frontend/src/lib/longpress/` - Longpress detection
  - `use-longpress.ts` - Longpress hook (1.5s duration)
- `frontend/src/lib/force-layout/` - Force layout positioning
  - `use-force-layout.ts` - D3-force simulation hook
- `frontend/src/lib/metaball/` - Metaball merge (may reuse from physics-cells)
  - `metaball-filter.tsx` - SVG filter component

**CRITICAL: Component Isolation**
- Each subcomponent MUST be in separate file
- Use React.lazy() and Suspense for mode-specific components
- Do NOT import all components in main page.tsx (prevents useless re-renders)
- Separate state for each mode to prevent cross-mode re-renders

**Modified Files**:
- `frontend/src/types/library.ts` - Add `MorphingCentralIsland` to `LibraryComponent`
- `frontend/src/lib/navigation/library-routes.ts` - Add `ROUTES.MORPHING_CENTRAL_ISLAND`
- `frontend/src/app/library/page.tsx` - Add morphing-central-island card
- `frontend/src/app/library/morphing-central-island/page.tsx` - Demo page (NEW)

### Dependencies

**New Dependencies**:
- `d3-force` - Force simulation for cell positioning (already in R014)
- `framer-motion` - Spring physics, drag, animations (already in use)
- `react-use-gesture` - (OPTIONAL) Enhanced gesture detection, or use Framer Motion drag

**Reused Patterns**:
- Metaball filter from `physics-cells-voice` component
- Force layout from `R014_ui_showcase/ForceGraphLayout`
- Widget types from `R014_ui_showcase/widget-types`

### API Integration

**WebSocket Messages** (for Voice mode widget spawning):
- Backend → Frontend: `{ type: "widget", descriptor: UIDescriptor, sessionId: string }`
- Frontend → Backend: Cell position updates (drag events), dismiss events

### Browser APIs Used

- **Web Audio API** - Already in use for voice mode (from physics-cells-voice)
- **getUserMedia** - Camera mode (new)
- **Haptic Feedback API** - Vibration at 1.0s during longpress (navigator.vibrate)
- **Clipboard API** - (OPTIONAL) For quick text paste in chat mode

### Performance Considerations

- **D3-force simulation**: Run once on cell count change, memoize positions
- **Metaball filter**: Single SVG filter on parent group (not per-cell)
- **Cilia animations**: Use CSS transforms (GPU accelerated)
- **requestAnimationFrame loop**: For voice mode cell physics (reuse pattern from physics-cells)
- **Component Isolation**: CRITICAL - Each subcomponent in separate file, lazy-loaded to prevent useless re-renders
  - Do NOT import all components in main page.tsx
  - Use React.lazy() and Suspense for mode-specific components
  - Separate state for each mode to prevent cross-mode re-renders

### Accessibility

- **Keyboard navigation**: Tab through mode islands, Enter to select
- **Screen reader**: Announce mode changes, cell emergence/dismiss
- **Touch targets**: Minimum 44px for mobile (mode islands, nucleus)
- **Haptic alternatives**: Visual-only fallback when vibration not supported

---

## Summary

This change establishes the **Morphing Central Island** as AGENTX's primary generative UI pattern - a minimal, organic interface that transforms based on user intent through gesture and mode selection. The biological metaphors (cell engulfing, cilia typing, metaball merging) create a cohesive, living UI that responds naturally to user interaction.

The 13 granular specs ensure every detail is preserved during implementation, from the exact timing of longpress feedback to the hair texture on cilia filaments. Each spec follows the **LOOKS / WORKS / LAYOUT** structure, making implementation straightforward while preventing detail loss.

**Next**: Design phase will elaborate on component architecture, state management, and integration patterns.
