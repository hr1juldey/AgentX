# C008 Organic UI Requirements Report

Based on analysis of archived C008 (organic-ui) OpenSpec change.

## 1. Implementation Status from tasks.md

### ✅ COMPLETED Tasks:
- **Phase 1: Design Token System** - tokens.ts (129 lines, 11 categories), motion.ts (9 presets)
- **Phase 2: Primitive Components** - Cell, Nucleus components implemented
- **Phase 3: Voice Nucleus** - VoiceButton with platform-aware sizing (~180 lines)
- **Phase 4: Metaball System** - SVG goo filter, physics engine
- **Phase 5: Integration** - agent directory, widget registry, LangGraph integration

### ⬜ PENDING Tasks:
- Testing on desktop (160px size)
- Testing on mobile (72px size)
- Testing reduced motion preference
- Metaball desktop testing (16px blur, 12 blobs)
- Metaball mobile testing (12px blur, 6 blobs)
- Accessibility audit (Axe DevTools)
- Performance audit (Lighthouse)
- Real device testing

## 2. Metaball System Requirements (CRITICAL)

### Core Architecture:
- **Implementation**: SVG goo filter (not WebGL/Canvas)
- **Z-index**: layer.metaball (1) - above background, below widgets
- **Pointer events**: none (doesn't block interactions)

### Platform-Aware Configuration:
- **Desktop**: 16px blur, 12 blobs maximum
- **Mobile**: 12px blur, 6 blobs maximum
- **Physics**: Full on desktop, attraction-only on mobile

### Performance Requirements:
- **Desktop**: ≥60fps with 12 blobs
- **Mobile**: ≥30fps with 6 blobs
- **Auto-disable**: When FPS <20 for 3 consecutive seconds
- **Graceful degradation**: Falls back to clean circles when disabled

### SVG Goo Filter (Locked Implementation):
```svg
<filter id="goo">
  <feGaussianBlur in="SourceGraphic" stdDeviation={config.blur} result="blur" />
  <feColorMatrix in="blur" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 24 -10" />
</filter>
```

### Physics Engine:
- **Attraction**: Spring toward anchor point (0.02)
- **Repulsion**: Push away from other blobs (0.05) - disabled on mobile
- **Viscosity**: Friction (0.3)
- **Max speed**: 2

## 3. Design Token System Requirements

### 11 Token Categories:
1. **color** - Biological theme (void, membrane, cytoplasm, organelle, nucleus, protein, ghost, enzyme, mitosis, apoptosis)
2. **radius** - Cell-based radii (cell, bubble, lg, md, sm, xs)
3. **space** - Organic spacing (nucleus, cell, tissue, organ, organism, colony, ecosystem)
4. **shadow** - Biological shadows (cell, float, deep, glow, pulse)
5. **blur** - Blur levels (light, medium, heavy)
6. **font** - Typography (family, size, weight, leading)
7. **timing** - Animation timing (instant, quick, normal, spawn, morph, drift)
8. **easing** - Organic curves (cell, elastic, anticipate, exit)
9. **metaball** - Physics constants (threshold, viscosity, attraction, repulsion, maxSpeed)
10. **widget** - Widget sizes (micro, small, medium, large, hero)
11. **layer** - Z-index layers (bg, metaball, surface, widget, float, voice, modal, toast)

## 4. Voice Nucleus Requirements (CRITICAL)

### Sizing & Positioning:
- **Desktop**: 160px diameter, centered position
- **Mobile**: 72px diameter, fixed bottom-center (24px from bottom)
- **Touch target**: 72px (exceeds 44px WCAG minimum)

### Animations:
- **Pulse** (active state): Scale [1, 1.08, 1], Shadow [glow, pulse, glow], Duration 1.4s
- **Drift** (idle state): Movement y [0, -8, 0], x [0, 4, 0], Duration 2.4s

### Accessibility:
- **Keyboard**: Tab to focus, Space to toggle
- **Screen reader**: "Start speaking" / "Stop speaking" labels
- **ARIA**: `aria-pressed` reflects state
- **Reduced motion**: All animations disabled
- **Focus ring**: `focus-visible:ring-2 ring-enzyme`

### Z-index:
- **layer.voice**: 40 (above widgets, below modals)

## 5. Motion Presets Requirements

### 9 Core Presets:
1. **mitosis** - Widget spawning (380ms, elastic ease)
2. **pulse** - Voice active state (1.4s, infinite)
3. **drift** - Idle floating (2.4s, infinite)
4. **lift** - Hover effect (150ms)
5. **compress** - Tap effect (80ms)
6. **drag** - Dragging state (z-index 40)
6. **morph** - Shape transformation (520ms, cell ease)
7. **stream** - Text streaming (150ms, anticipate ease)
8. **interrupt** - Attention signal (400ms, elastic ease)

## 6. Integration Requirements

### Architecture Pattern:
- **Server-driven UI**: LangGraph backend → push_ui_message() → Frontend
- **Widget registry**: ui.tsx colocated with graph.py
- **Component colocation**: Industry standard (LangSmith pattern)

### Data Flow:
1. Backend emits widget via `push_ui_message("card", {...})`
2. Frontend receives via `useStream()` and `LoadExternalComponent`
3. Widget renders with Organic UI (tokens + motion + metaballs)
4. Voice nucleus spawns widgets with mitosis animation

## 7. Acceptance Criteria Summary

### Functional Criteria (12):
- Design tokens defined (11 categories)
- Platform-aware metaballs (16px/12px blur, 12/6 blobs)
- Voice nucleus sizing (160px/72px)
- Pulse animation (1.4s breathing)
- Drift animation (2.4s floating)
- Keyboard accessibility
- Screen reader support
- Reduced motion support
- Auto-disable at FPS <20
- Graceful degradation
- WCAG AA compliance
- Biological metaphor consistency

### Non-Functional Criteria (9):
- Desktop performance ≥60fps
- Mobile performance ≥30fps
- Bundle size <50KB
- Token coverage 100%
- File size limits
- Type safety 0 errors
- Accessibility 0 critical issues
- Import rules compliance
- Visual consistency
