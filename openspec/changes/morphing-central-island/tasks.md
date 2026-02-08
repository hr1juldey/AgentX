# Tasks: Morphing Central Island

Implementation tasks organized for incremental building with frontend-design skill integration.

**CRITICAL CONSTRAINT**: Existing `physics-cells-voice` component and `/library/physics-cells` page MUST remain untouched. All new code is created in separate `central-island/` directory.

---

## 1. Foundation & Infrastructure (Copy & Adapt)

### 1.1 Copy Physics Core Components

- [ ] 1.1.1 Copy `frontend/src/lib/physics/metaball-filter.tsx` to `frontend/src/lib/physics/central-island/metaball-filter.tsx`
- [ ] 1.1.2 Copy `frontend/src/lib/physics/spring-damping.ts` to `frontend/src/lib/physics/central-island/spring-damping.ts`
- [ ] 1.1.3 Copy `frontend/src/lib/physics/physics-renderer.tsx` to `frontend/src/lib/physics/central-island/physics-renderer.tsx`
- [ ] 1.1.4 DO NOT modify original physics-cells-voice files (constraint check)
- [ ] 1.1.5 Run `ruff check --fix` and `ruff format .` on copied files

### 1.2 Create Central Island Directory Structure

- [ ] 1.2.1 Create `frontend/src/components/central-island/` directory
- [ ] 1.2.2 Create `frontend/src/components/central-island/nucleus/` subdirectory
- [ ] 1.2.3 Create `frontend/src/components/central-island/mode-islands/` subdirectory
- [ ] 1.2.4 Create `frontend/src/components/central-island/voice-mode/` subdirectory
- [ ] 1.2.5 Create `frontend/src/components/central-island/chat-mode/` subdirectory
- [ ] 1.2.6 Create `frontend/src/components/central-island/cilia/` subdirectory
- [ ] 1.2.7 Create `frontend/src/components/central-island/progress/` subdirectory

### 1.3 Create Library Routing

- [ ] 1.3.1 Add `MORPHING_CENTRAL_ISLAND` to `frontend/src/types/library.ts`
- [ ] 1.3.2 Add route constant to `frontend/src/lib/navigation/library-routes.ts`
- [ ] 1.3.3 Verify route does NOT conflict with existing physics-cells route

---

## 2. Nucleus & Longpress (frontend-design skill)

### 2.1 Build Nucleus Component (frontend-design: "minimalist circular nucleus button, 60px, subtle pulse animation when idle, accelerates during 1.5s longpress")

- [ ] 2.1.1 Use `/skill:frontend-design` to create `frontend/src/components/central-island/nucleus.tsx`
- [ ] 2.1.2 Tell frontend-design: "Circular button, 60px diameter, white background (#FFFFFF), centered in viewport, subtle pulse animation (scale 1.0 → 1.05 → 1.0, 3s duration), when idle state"
- [ ] 2.1.3 Tell frontend-design: "Add `data-nucleus-state='idle'` attribute for state tracking"
- [ ] 2.1.4 Tell frontend-design: "Use Framer Motion for pulse animation (AnimatePresence for state changes)"
- [ ] 2.1.5 Tell frontend-design: "Position: fixed, bottom: 25%, left: 50%, transform: translateX(-50%)"

### 2.2 Implement Longpress Detection Hook

- [ ] 2.2.1 Create `frontend/src/lib/longpress/use-longpress.ts` hook
- [ ] 2.2.2 Implement 1500ms duration with progress tracking
- [ ] 2.2.3 Add 1000ms haptic feedback trigger (`navigator.vibrate(200)`)
- [ ] 2.2.4 Implement cancel detection: move away > 50px OR click free space
- [ ] 2.2.5 Return `{ isLongpressActive, longpressProgress, bind }` interface

### 2.3 Build Longpress Pulse Animation

- [ ] 2.3.1 Update nucleus.tsx to use `useLongpress` hook
- [ ] 2.3.2 Implement pulse acceleration during longpress (3000ms → 500ms duration)
- [ ] 2.3.3 Add visual feedback: pulse gets faster as longpress progresses
- [ ] 2.3.4 NO progress ring (that's separate backend-progress-indicator spec)

### 2.4 Mode Islands Spawning (frontend-design: "4 circular islands spawn from nucleus in cardinal directions: Voice (top, purple), Chat (left, blue), File (right, green), Camera (bottom, orange)")

- [ ] 2.4.1 Use `/skill:frontend-design` to create `frontend/src/components/central-island/mode-islands.tsx`
- [ ] 2.4.2 Tell frontend-design: "4 circular islands, 48px diameter, spawn from nucleus center at 1500ms longpress, cardinal positions: Voice (top: -80px), Chat (left: -80px), File (right: -80px), Camera (bottom: -80px)"
- [ ] 2.4.3 Tell frontend-design: "Island colors: Voice=Purple (#C792EA), Chat=Blue (#82AAFF), File=Green (#64FFDA), Camera=Orange (#FF6B35)"
- [ ] 2.4.4 Tell frontend-design: "Island icons: Mic (Voice), MessageCircle (Chat), FileText (File), Camera (Camera) from Lucide React, 24px white icons"
- [ ] 2.4.5 Tell frontend-design: "Spring emergence animation: stiffness 200, damping 25, duration ~200ms, scale 0 → 1"
- [ ] 2.4.6 Tell frontend-design: "Islands only visible when isLongpressActive=true"

### 2.5 Mode Islands Click Detection

- [ ] 2.5.1 Implement click detection on mode islands
- [ ] 2.5.2 Click triggers sequential collapse (see Section 3)
- [ ] 2.5.3 Click feedback: scale 1.0 → 0.95 → 1.0 (press effect)
- [ ] 2.5.4 Fix R014 bug: track dragDistance, only onClick if dragDistance < 5px

---

## 3. Sequential Collapse (Builds on Existing Physics)

### 3.1 Sequential Collapse Animation (reuse metaball-filter.tsx)

- [ ] 3.1.1 Use `/skill:frontend-design` to create `frontend/src/components/central-island/sequential-collapse.tsx`
- [ ] 3.1.2 Tell frontend-design: "Sequential collapse: non-selected islands slide one-by-one toward selected island and merge via metaball effect"
- [ ] 3.1.3 Tell frontend-design: "Collapse sequence (when Voice selected): Chat slides first (200ms), File slides second (200ms after Chat), Camera slides third (200ms after File)"
- [ ] 3.1.4 Tell frontend-design: "Spring animation: stiffness 400, damping 20, snappy with elastic bounce"
- [ ] 3.1.5 Tell frontend-design: "Use copied metaball-filter.tsx for gooey merge effect (blur 16px, color matrix '1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -7')"

### 3.2 Elastic Bounce After Absorption

- [ ] 3.2.1 Implement bounce animation on selected island after each merge
- [ ] 3.2.2 Bounce: scale 1.0 → 1.15 → 1.0 (150ms duration, 2-3 oscillations)
- [ ] 3.2.3 Final merge bounce is larger: scale 1.0 → 1.2 → 1.0 (200ms duration)
- [ ] 3.2.4 Spring: stiffness 500, damping 15

### 3.3 Nucleus Absorption Complete

- [ ] 3.3.1 Single nucleus remains after all islands absorbed
- [ ] 3.3.2 Nucleus takes selected mode's color (Voice=purple, Chat=blue, File=green, Camera=orange)
- [ ] 3.3.3 Nucleus scale increases slightly (1.0 → 1.1) to indicate mode active

---

## 4. Nucleus Morph (Chat Mode Only)

### 4.1 Circle to Bar Morph (frontend-design: "Chat nucleus morphs from 60px circle to 400px × 50px rounded bar")

- [ ] 4.1.1 Use `/skill:frontend-design` to create chat bar structure
- [ ] 4.1.2 Tell frontend-design: "Phase 1: Circle (60px) → Bar (400px × 50px), Spring: stiffness 300, damping 30, Duration: 150ms"
- [ ] 4.1.3 Tell frontend-design: "Border-radius morphs: 30px (circle) → 25px (rounded pill bar)"
- [ ] 4.1.4 Tell frontend-design: "Bar color: --color-actin (#82AAFF blue), centered horizontally, max-width 400px"
- [ ] 4.1.5 Tell frontend-design: "Mobile: 90% viewport width (max 400px)"

### 4.2 Paper Section Emergence (frontend-design: "Paper section expands upward from bar AFTER bar morph completes")

- [ ] 4.2.1 Tell frontend-design: "Phase 2: Wait 150ms after bar morph, then paper expands upward from bar"
- [ ] 4.2.2 Tell frontend-design: "Paper: 0-100px height (auto-adjusts), background: --color-cell (#1E1E1E dark)"
- [ ] 4.2.3 Tell frontend-design: "Paper initially empty, only shows current input (not chat history)"
- [ ] 4.2.4 Tell frontend-design: "Spring expansion: stiffness 250, damping 25, duration ~150ms"

---

## 5. Enhanced Energy Accumulator (ADAPTS existing, throws functional widgets)

### 5.1 Copy & Adapt Energy Accumulator

- [ ] 5.1.1 Copy `frontend/src/lib/physics/energy-accumulator.ts` to `frontend/src/lib/physics/central-island/energy-accumulator.ts`
- [ ] 5.1.2 ADAPT for widget spawning: Replace audio energy → mock timer (3-5s intervals for library demo)
- [ ] 5.1.3 ADAPT: Accumulate "widget spawn energy" (not audio energy)
- [ ] 5.1.4 Return type: Same API but triggers widget spawn instead of satellite cell movement

### 5.2 Widget Cell Spawning (NEW CAPABILITY - key enhancement)

- [ ] 5.2.1 Create mock widget spawner: Randomly select widget type (Chart/Form/Image)
- [ ] 5.2.2 Spawn interval: Every 3-5 seconds randomly
- [ ] 5.2.3 Widget types: ChartWidget, FormWidget, ImageWidget (from R014, reuse components)
- [ ] 5.2.4 Each spawn triggers: nucleus pulse → bud formation → separation → travel → arrival

### 5.3 Widget Cell Energy (NEW - cells don't auto-return)

- [ ] 5.3.1 ADAPT energy-accumulator: Widget cells start with energy 1.0 (high)
- [ ] 5.3.2 Widget cells maintain position (don't orbit back to nucleus)
- [ ] 5.3.3 Only return to nucleus via manual drag-to-center dismiss
- [ ] 5.3.4 This is KEY DIFFERENCE from physics-cells-voice (satellites auto-returned)

---

## 6. Enhanced Orbit Mechanics (ADAPTS existing for widget cells)

### 6.1 Copy & Adapt Orbit Physics

- [ ] 6.1.1 Copy `frontend/src/lib/physics/orbit-physics.ts` to `frontend/src/lib/physics/central-island/orbit-physics.ts`
- [ ] 6.1.2 ADAPT for widget cells: Add `widgetCell: boolean` flag to CellState
- [ ] 6.1.3 Widget cells: Fixed position (not orbiting), high energy (1.0)
- [ ] 6.1.4 Non-widget cells: Keep original orbit behavior (low energy, auto-return)

### 6.2 Cell Trajectory for Widgets

- [ ] 6.2.1 ADAPT orbit-physics: Add `calculateWidgetTrajectory()` function
- [ ] 6.2.2 Widget trajectory: Direct line from nucleus edge → force-layout position
- [ ] 6.2.3 Spring stiffness: 150 (softer), damping: 20 (bouncy)
- [ ] 6.2.4 Duration: ~400ms travel + 200ms arrival bounce

---

## 7. Voice Mode - Nucleus & Cell Widgets

### 7.1 Voice Nucleus with Mic Toggle (frontend-design: "Circular nucleus with mic icon in center, toggle on/off")

- [ ] 7.1.1 Use `/skill:frontend-design` to create `frontend/src/components/central-island/voice-mode/voice-nucleus.tsx`
- [ ] 7.1.2 Tell frontend-design: "Circular nucleus, 60px diameter, background: --color-endoplasmic (#C792EA purple)"
- [ ] 7.1.3 Tell frontend-design: "Mic icon in center: 28px, white (#FFFFFF), MicOff when off, Mic when on"
- [ ] 7.1.4 Tell frontend-design: "Mic OFF state: icon opacity 0.7, slow pulse (3000ms)"
- [ ] 7.1.5 Tell frontend-design: "Mic ON state: icon opacity 1.0, fast pulse (1000ms), glow effect (box-shadow, --color-golgi #FFD700)"
- [ ] 7.1.6 Tell frontend-design: "Click to toggle, request mic permission on first ON"

### 7.2 Cell Bud Formation (frontend-design: "Small bud forms on nucleus edge, 20px, matches widget color")

- [ ] 7.2.1 Tell frontend-design: "20px circle bud appears on nucleus edge at random angle (0-360°)"
- [ ] 7.2.2 Tell frontend-design: "Bud color matches widget type (Chart=purple, Form=blue, Image=green)"
- [ ] 7.2.3 Tell frontend-design: "Metaball connection to nucleus during bud phase (200ms)"
- [ ] 7.2.4 Tell frontend-design: "Nucleus pulse (scale 1.0 → 1.1 → 1.0) before bud appears"

### 7.3 Cell Separation & Travel

- [ ] 7.3.1 Implement cell separation using adapted orbit-physics
- [ ] 7.3.2 Cell travels ~200px from nucleus edge to force-layout position
- [ ] 7.3.3 Spring trajectory: stiffness 150, damping 20, ~400ms travel
- [ ] 7.3.4 May slightly overshoot target then settle

### 7.4 Cell Arrival Bounce

- [ ] 7.4.1 Implement bounce when cell arrives at target position
- [ ] 7.4.2 Bounce: scale 1.0 → 1.15 → 1.0 (150ms, 2 oscillations)
- [ ] 7.4.3 Spring: stiffness 400, damping 15

### 7.5 Force Layout for Widget Cells

- [ ] 7.5.1 Copy D3-force layout pattern from R014_ui_showcase
- [ ] 7.5.2 Dynamic radius: 1-4 cells (160px), 5-8 cells (200px), 9-12 cells (240px)
- [ ] 7.5.3 Forces: radial (0.8), charge (-50), collide (radius + 8), center (0.1)
- [ ] 7.5.4 Memoize positions (only recalculate on cell count change)

### 7.6 Draggable Cells (frontend-design: "Cells are draggable, click vs drag fixed")

- [ ] 7.6.1 Use `/skill:frontend-design` to make cells draggable
- [ ] 7.6.2 Tell frontend-design: "Framer Motion drag: whileDrag={{ scale: 1.05, cursor: 'grabbing', zIndex: 50 }}"
- [ ] 7.6.3 Tell frontend-design: "Click vs drag detection: Track dragDistance from onMouseDown, only onClick if dragDistance < 5px (FIXES R014 BUG)"
- [ ] 7.6.4 Tell frontend-design: "Viewport bounds checking: Prevent cell from being dragged off-screen"
- [ ] 7.6.5 Tell frontend-design: "Z-index: Dragging=50, At rest=10"

### 7.7 Cell Sticky Edges (reuse metaball-filter.tsx)

- [ ] 7.7.1 Apply metaball filter when cells are within 40px of each other
- [ ] 7.7.2 Sticky threshold: 40px (desktop), 32px (mobile)
- [ ] 7.7.3 Gooey bridge appears between cells
- [ ] 7.7.4 Cells appear to stick together like biological cells

### 7.8 Cell Dismiss - Drag to Center (frontend-design: "Drag cell toward nucleus to dismiss")

- [ ] 7.8.1 Implement 150px dismiss threshold (distance to nucleus center)
- [ ] 7.8.2 Tell frontend-design: "Visual feedback when approaching 150px: nucleus pulse accelerates, glow appears"
- [ ] 7.8.3 Tell frontend-design: "When distance < 150px: cell automatically animates toward nucleus, user can release"
- [ ] 7.8.4 Tell frontend-design: "Metaball merge on contact, cell shrinks (scale 1 → 0.5 → 0), nucleus absorbs (scale 1 → 1.2 → 1, elastic bounce)"
- [ ] 7.8.5 Constraint: Drag AWAY from nucleus → cell stays, Swipe-away → NO

---

## 8. Chat Mode - Biological Typewriter

### 8.1 Keyboard Input Section (frontend-design: "Bottom input section, stable, 50px height, constrained 400px")

- [ ] 8.1.1 Tell frontend-design: "Input field at bottom of chat bar, 50px height, full width minus send button"
- [ ] 8.1.2 Tell frontend-design: "Background: --color-membrane (#141414), text color: --color-nucleus (#FFFFFF)"
- [ ] 8.1.3 Tell frontend-design: "Placeholder: 'Type or speak your message...', placeholder color: --color-vacuole (#666666)"
- [ ] 8.1.4 Tell frontend-design: "No border (integrated into bar), border-radius 25px on bottom corners only"

### 8.2 Send Button (frontend-design: "Send button at right, triggers message send")

- [ ] 8.2.1 Tell frontend-design: "Button at right side, 60px width, height matches section (50px)"
- [ ] 8.2.2 Tell frontend-design: "Background: --color-actin (#82AAFF), text: Send (white), border-radius: 25px on right corners"
- [ ] 8.2.3 Tell frontend-design: "Hover: brightness +10%, Disabled (empty input): opacity 0.5, cursor: not-allowed"
- [ ] 8.2.4 Send action: Input clears, all cilia retract, message bubbles up as floating cell

### 8.3 Horizontal Divider (frontend-design: "1px line that holds cilia, separates paper and keyboard")

- [ ] 8.3.1 Tell frontend-design: "1px horizontal line, color: --color-membrane (#141414)"
- [ ] 8.3.2 Tell frontend-design: "Position: between paper (top) and keyboard (bottom) sections"
- [ ] 8.3.3 Tell frontend-design: "Cilia base points are anchored along this line"

### 8.4 Paper Display Section (frontend-design: "Top section shows current input, 0-100px height, expands upward")

- [ ] 8.4.1 Tell frontend-design: "Top section of chat bar, shows current input only (not chat history)"
- [ ] 8.4.2 Tell frontend-design: "Background: --color-cell (#1E1E1E), expands upward from divider"
- [ ] 8.4.3 Tell frontend-design: "Initially empty (height 0), expands when user types, auto-adjusts height"
- [ ] 8.4.4 Tell frontend-design: "Max height ~100px, scrollable if content exceeds"

### 8.5 Cilia Filament with Hair Texture (frontend-design: "Hair-texture filaments extend from divider, hammer animation per keystroke")

- [ ] 8.5.1 Use `/skill:frontend-design` to create cilia filament component
- [ ] 8.5.2 Tell frontend-design: "Filament extends UPWARD from horizontal divider, 2-4px width, hair texture (not smooth line)"
- [ ] 8.5.3 Tell frontend-design: "Hair texture options: CSS background pattern (repeating-linear-gradient) OR SVG filter (turbulence + displacement)"
- [ ] 8.5.4 Tell frontend-design: "Filament color: --color-enzyme (#00D9FF cyan), hair texture color matches filament"

### 8.6 Hammer Strike Animation (frontend-design: "Per-keystroke cchunk + bounce, 150ms total")

- [ ] 8.6.1 Tell frontend-design: "Each keystroke → cilium performs hammer-strike animation"
- [ ] 8.6.2 Tell frontend-design: "Animation: Scale 0 → 1.2 → 1.0 (cchunk + bounce)"
- [ ] 8.6.3 Tell frontend-design: "Duration: 150ms total (100ms scale-up + 50ms bounce settle)"
- [ ] 8.6.4 Tell frontend-design: "Spring: stiffness 400, damping 20 (snappy with bounce)"

### 8.7 Cilia Reverse Retraction (frontend-design: "Backspace triggers reverse retraction, 100ms, ease-in")

- [ ] 8.7.1 Tell frontend-design: "When user backspaces, corresponding cilium retracts with reverse animation"
- [ ] 8.7.2 Tell frontend-design: "Animation: Scale 1.0 → 0.5 → 0 (rewind effect)"
- [ ] 8.7.3 Tell frontend-design: "Duration: 100ms (faster than extension), easing: ease-in (not spring)"
- [ ] 8.7.4 Tell frontend-design: "Hair texture shrinks with filament, maintains proportion"

### 8.8 Sent Message Float (frontend-design: "Sent message bubbles up and becomes floating cell")

- [ ] 8.8.1 Tell frontend-design: "When message sent (Send button click or Enter), input + paper clear"
- [ ] 8.8.2 Tell frontend-design: "Message bubbles up: translateY(+20px), ease-out, 200ms"
- [ ] 8.8.3 Tell frontend-design: "Message morphs to cell widget: gains border, shadow, metaball-ready styling"
- [ ] 8.8.4 Tell frontend-design: "Auto-positions in circle via force layout, becomes draggable cell, dismissible via drag-to-center"

---

## 9. Backend Progress Indicator (Kotlin port)

### 9.1 Metaball Progress Ring (frontend-design: "Rotating arc + 9 orbiting circles, metaball-wrapped")

- [ ] 9.1.1 Use `/skill:frontend-design` to create progress indicator
- [ ] 9.1.2 Tell frontend-design: "Ported from Kotlin ProgressLoader: 300px container, 250px rotating arc (215° sweep), 9 orbiting circles (50px each)"
- [ ] 9.1.3 Tell frontend-design: "Rotating arc: 0° → -360° (clockwise), 8000ms, linear easing, infinite loop"
- [ ] 9.1.4 Tell frontend-design: "Orbiting circles: 0° → 360° (counterclockwise), 8000ms, linear easing, 40° offset each"
- [ ] 9.1.5 Tell frontend-design: "Base color: --color-enzyme (#00D9FF cyan), arc/circles: --color-nucleus (#FFFFFF white)"
- [ ] 9.1.6 Tell frontend-design: "Metaball filter wrapper (blur 40px), only shows during backend processing (LangGraph, STT, widget generation)"

---

## 10. Library Integration

### 10.1 Create Demo Page (frontend-design: "Component demo page with controls")

- [ ] 10.1.1 Use `/skill:frontend-design` to create `frontend/src/app/library/morphing-central-island/page.tsx`
- [ ] 10.1.2 Tell frontend-design: "Demo page title: 'Morphing Central Island - Biological Generative UI'"
- [ ] 10.1.3 Tell frontend-design: "Demo container with central-island component centered in viewport"
- [ ] 10.1.4 Tell frontend-design: "Control panel with toggle: Mock widget spawning (default: ON), Mode selector buttons"
- [ ] 10.1.5 Tell frontend-design: "Debug mode: Show nucleus state, energy level, cell count labels"

### 10.2 Add Library Card

- [ ] 10.2.1 Add MorphingCentralIsland entry to `frontend/src/app/library/page.tsx` grid
- [ ] 10.22 Card layout: Thumbnail, title, description, "View Demo →" button
- [ ] 10.23 Use physics-cells thumbnail as placeholder (or create new thumbnail)
- [ ] 10.24 Link to `/library/morphing-central-island`

### 10.3 Verify physics-cells Page Untouched

- [ ] 10.3.1 Verify `frontend/src/app/library/physics-cells/page.tsx` is NOT modified
- [ ] 10.3.2 Verify `frontend/src/components/physics-cells-voice.tsx` is NOT modified
- [ ] 10.3.3 Verify physics-cells route still works: http://localhost:3015/library/physics-cells
- [ ] 10.3.4 Take screenshot of physics-cells page before and after for verification

---

## 11. Component Isolation & Performance

### 11.1 Lazy Load Mode Components

- [ ] 11.1.1 Create `frontend/src/components/central-island/index.ts` with lazy loaders
- [ ] 11.1.2 Lazy load: VoiceMode, ChatMode, CameraMode, FileMode components
- [ ] 11.1.3 Wrap in Suspense with loading fallback
- [ ] 11.1.4 This prevents re-rendering all modes when only one mode changes

### 11.2 Recoil State Setup

- [ ] 11.2.1 Install @recoiljs if not present
- [ ] 11.2.2 Create atoms: nucleusState, activeMode, voiceModeCells, chatModeInput, etc.
- [ ] 11.2.3 Per-mode atoms prevent cross-mode re-renders (only mode-specific components subscribe)
- [ ] 11.2.4 DO NOT use shared state that causes all components to re-render

### 11.3 Performance Optimization

- [ ] 11.3.1 Memoize force layout positions (only recalculate on cell count change)
- [ ] 11.3.2 Single SVG filter on parent group (not per-cell)
- [ 11.3.3 Use CSS transforms (GPU accelerated) for animations
- [ ] 11.3.4 requestAnimationFrame loop for voice mode cells (reuse physics-renderer pattern)
- [ ] 11.3.5 Run `ruff check --fix` and `ruff format .` on all new code

---

## 12. Testing & Verification

### 12.1 Navigation Tests

- [ ] 12.1.1 Test main → library → morphing-central-island navigation
- [ ] 12.1.2 Verify physics-cells page still works: http://localhost:3015/library/physics-cells
- [ ] 12.1.3 Test browser back/forward button support

### 12.2 Feature Tests

- [ ] 12.2.1 Test longpress (1.5s) → mode islands spawn
- [ ] 12.2.2 Test sequential collapse → single nucleus
- [ ] 12.2.3 Test mode selection → nucleus morph (Voice → circle, Chat → bar)
- [ ] 12.2.4 Test voice mode: Mock widget spawning → cells emerge → draggable → dismiss
- [ ] 12.2.5 Test chat mode: Typing → cilia extend → backspace retract → send → float cell

### 12.3 Cross-Browser Tests

- [ ] 12.3.1 Test on Chrome (primary development)
- [ ] 12.3.2 Test on Firefox (SVG filter compatibility)
- [ ] 12.3.3 Test on Safari (Framer Motion compatibility)
- [ ] 12.3.4 Test on mobile browsers (touch events, haptic feedback)

### 12.4 Performance Tests

- [ ] 12.4.1 Verify 60 FPS during all animations
- [ ] 12.4.2 Test with 12 cells (maximum expected count)
- [ ] 12.4.3 Profile memory usage (no leaks, proper cleanup)
- [ ] 12.4.4 Test mock widget spawning for 5 minutes (no performance degradation)

### 12.5 Verify Implementation

- [ ] 12.5.1 Run `/opsx:verify morphing-central-island` to check implementation against specs
- [ ] 12.5.2 Address any CRITICAL issues found
- [ ] 12.5.3 Review WARNING issues and address if applicable
- [ ] 12.5.4 Verify all 41 specs have corresponding implementation

---

## 13. Documentation

### 13.1 Code Documentation

- [ ] 13.1.1 Add JSDoc comments to all physics functions
- [ ] 13.1.2 Document component props API
- [ ] 13.1.3 Document frontend-design skill usage (what was requested vs implemented)

### 13.2 Thumbnail Creation

- [ ] 13.2.1 Create thumbnail for morphing-central-island card (`/public/library/thumbnails/morphing-central-island.png` or `.webp`)
- [ ] 13.2.2 Thumbnail shows: Nucleus with 4 mode islands, or Chat bar with cilia
- [ ] 13.2.3 Ensure thumbnail physics-cells page is NOT overwritten

### 13.3 Update CLAUDE.md

- [ ] 13.3.1 Document new central-island/ directory structure
- [ ] 13.3.2 Document adapted physics files (central-island/ subdirectory)
- [ ] 13.3.3 Add new capabilities to project documentation

---

## Task Summary

**Total Tasks**: 100+ tasks across 13 sections

**Implementation Order (Smart Sequence for frontend-design skill):**

1. **Foundation** (Section 1): Copy physics, create directory structure - NO changes to existing code
2. **Nucleus & Longpress** (Section 2): Build idle nucleus, longpress, mode spawning - Can test standalone
3. **Sequential Collapse** (Section 3): Add collapse animation - Extends nucleus component
4. **Nucleus Morph** (Section 4): Add chat bar morph - Extends nucleus component
5. **Enhanced Energy** (Section 5): KEY ENHANCEMENT - Widget cells (not just satellites)
6. **Enhanced Orbit** (Section 6): Adapt for widget cells (higher energy, no auto-return)
7. **Voice Mode** (Section 7): Complete voice mode with widgets - Full feature demonstration
8. **Chat Mode** (Section 8): Biological typewriter - Unique feature demonstration
9. **Progress** (Section 9): Backend indicator - Visual polish
10. **Library** (Section 10): Demo page and card - Make accessible
11. **Isolation** (Section 11): Performance optimization
12. **Testing** (Section 12): Comprehensive verification
13. **Docs** (Section 13): Complete documentation

**frontend-design Skill Invocations:** 15+ calls to `/skill:frontend-design` with specific design instructions for each component.

**Key Constraints:**
- ✅ Original physics-cells-voice component stays untouched
- ✅ Original physics-cells demo page stays untouched
- ✅ All new code in `central-island/` directory
- ✅ Copied physics files adapted (not modified) in `central-island/` subdirectory

**Definition of Done**: All tasks complete, `/opsx:verify` passes with no CRITICAL issues, physics-cells page verified unchanged.
