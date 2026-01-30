# Proposal: c008-organic-ui

**Generated**: 2026-01-29
**Change**: c008-organic-ui
**Schema**: spec-factory v1.0.0

---

## Summary

Implement the Organic UI visual layer for AgentX v0.1, featuring a bio-inspired design system with platform-aware metaballs, a central voice nucleus, and comprehensive design tokens. This change provides the visual skin that sits on top of the LangGraph server-driven UI architecture established in C007.

---

## Motivation

### Problem Statement

Current UI prototypes (R014) lack:
1. **Performance optimization** - Fixed blur and blob limits cause issues on mobile devices
2. **Visual consistency** - No single source of truth for design tokens
3. **Platform awareness** - One-size-fits-all approach doesn't adapt to device capabilities
4. **Biological metaphor** - UI doesn't convey the "living organism" concept that's core to AgentX

### Current State

R014 UI showcase provides:
- 12 widget types with callback-based delivery (replaced by LangGraph in C007)
- Fixed 16px blur on all devices (too heavy for mobile)
- No blob limits (can spawn infinite widgets)
- Central voice island (160px) but no platform-aware sizing
- Basic animations without biological metaphors

### Desired State

C008 Organic UI delivers:
- **Platform-aware metaballs**: 16px blur (desktop), 12px blur (mobile), 6 blobs max (mobile), 12 blobs max (desktop)
- **Single source of truth**: `design/tokens.ts` powers CSS variables and Tailwind config
- **Biological metaphor**: All elements named after biological concepts (nucleus, cell, membrane, enzyme)
- **Voice nucleus**: 160px desktop, 72px mobile with pulse/drift animations
- **Graceful degradation**: Auto-disable on struggling devices, falls back to clean circles

---

## Scope

### In Scope

- **Design token system** (`design/tokens.ts`): Colors, spacing, typography, shadows, blur, timing, easing, metaball physics, widget sizes, z-index layers
- **Capability detection**: Platform detection (isMobile), reduced motion preference, metaball config
- **Metaball system**: SVG goo filter, platform-aware blur, spring physics, performance monitoring
- **Voice nucleus component**: Platform-aware sizing (160px/72px), positioning (center/bottom-center), pulse/drift animations
- **Motion presets**: 9 reusable presets (mitosis, pulse, drift, lift, compress, drag, morph, stream, interrupt) + stagger
- **Primitive components**: Cell (glass surface), Nucleus (circular container), StreamText (text streaming animation)
- **CSS variables**: Auto-generated from tokens for global styles
- **Tailwind integration**: Extend Tailwind config with tokens
- **Accessibility**: Keyboard navigation, screen reader support, reduced motion mode

### Out of Scope

- **Widget rendering logic**: Handled by LangGraph `LoadExternalComponent` (C007)
- **WebSocket connection**: Handled by C004 voice-streaming
- **Audio capture/playback**: Handled by C004 voice-streaming
- **Backend API**: No new REST endpoints or WebSocket channels
- **Layout system**: Widget anchors and mobile stack deferred to C009 ui-polish
- **Component library**: Full shadcn/ui integration deferred to C009 ui-polish

### Dependencies

| Change | Status | Required For |
|--------|--------|--------------|
| **C007-frontend-architecture** | Pending | LangGraph server-driven UI pattern (`push_ui_message()`, `LoadExternalComponent`) |
| **C003-agent-pipeline** | Done | LangGraph state management with `ui_message_reducer` |
| **C004-voice-streaming** | Done | Voice WebSocket for audio streaming |

---

## Success Criteria

1. **Platform-Aware Performance**: Metaballs render at 60fps on desktop, 30fps on mobile
   - Measure: FPS monitoring during widget spawning (6 widgets mobile, 12 desktop)
   - Target: Desktop ≥60fps, Mobile ≥30fps, Auto-disable when FPS <20

2. **Design Token Coverage**: All UI elements reference tokens (no hardcoded values)
   - Measure: Code review for magic numbers/strings
   - Target: 100% token coverage for colors, spacing, typography, timing

3. **Platform Adaptation**: UI adapts to device capabilities
   - Measure: Test on desktop (≥1440px), tablet (1024px), mobile (≤640px)
   - Target: Correct sizing and blur on all platforms

4. **Accessibility Compliance**: WCAG AA standards met
   - Measure: Axe DevTools audit, keyboard navigation test, screen reader test
   - Target: Zero critical accessibility issues

5. **Graceful Degradation**: System degrades gracefully on low-end devices
   - Measure: Test on throttled CPU (4x slowdown)
   - Target: Auto-disable metaballs when FPS <20, falls back to clean circles

6. **Visual Consistency**: Biological metaphor applied consistently
   - Measure: Visual audit of all components
   - Target: All elements use biological naming (nucleus, cell, membrane, enzyme)

---

## Implementation Approach

### High-Level Approach

**Phase 1: Foundations** (Day 1)
- Create `design/tokens.ts` with all locked definitions from LLD
- Generate CSS variables in `globals.css`
- Extend Tailwind config with tokens
- Build primitive components (Cell, Nucleus, StreamText)

**Phase 2: Motion Presets** (Day 1)
- Create `design/motion.ts` with 9 presets + stagger
- Integrate with Framer Motion
- Test all animations with reduced motion preference

**Phase 3: Metaball System** (Day 2)
- Implement SVG goo filter with platform-aware blur
- Build physics engine (attraction, repulsion, viscosity)
- Add performance monitoring and auto-disable
- Test on desktop and mobile

**Phase 4: Voice Nucleus** (Day 2)
- Build VoiceButton component with platform-aware sizing
- Implement pulse/drift animations
- Add keyboard and screen reader support
- Test touch target compliance (44px minimum)

**Phase 5: Integration** (Day 3)
- Integrate with LangGraph server-driven UI (C007)
- Test widget spawning via `push_ui_message()`
- Verify metaball merging with multiple widgets
- Test on real devices (desktop, tablet, mobile)

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| **SVG goo filter for metaballs** | Works on all platforms, GPU-accelerated, lightweight | WebGL (too heavy), Canvas (complex to implement) |
| **Platform-aware blur (16px/12px)** | 25% less GPU load on mobile, maintains visual consistency | Fixed blur (too heavy on mobile), disabled on mobile (loses visual language) |
| **Blob limits (12 desktop, 6 mobile)** | 50% less computation on mobile, prevents performance degradation | No limits (infinite spawn problems), fixed limit everywhere (over-constraining desktop) |
| **Single source of truth tokens** | Change one file, entire UI updates; prevents drift | Multiple config files (DRY violation), CSS-only (no TypeScript type safety) |
| **Biological naming convention** | Conveys "living organism" concept, makes code self-documenting | Generic names (loses metaphor), technical names (less intuitive) |
| **Framer Motion for animations** | Industry standard, excellent TypeScript support, declarative API | CSS animations (limited capabilities), React Spring (less popular) |
| **Graceful degradation** | Ensures usability on low-end devices, doesn't gate functionality | Hard requirement (excludes users), performance cliffs (janky UX) |

### Constraints

- **Ports**: No new ports (uses frontend port 3000 from C007)
- **File size**:
  - `design/tokens.ts`: ~180 lines (acceptable for config file)
  - `design/motion.ts`: ~150 lines (acceptable for config file)
  - Component files: Max 100 lines each
- **Imports**: Absolute imports only (`@/design/tokens`, `@/design/motion`)
- **Dependencies**: Must wait for C007 completion (LangGraph integration)
- **Browser support**: Modern browsers only (Chrome 90+, Safari 14+, Firefox 88+, Edge 90+)

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Metaball performance on low-end mobile** | Medium | Medium | Platform-aware optimization (12px blur, 6 blobs, simplified physics), auto-disable when FPS <20 |
| **SVG goo filter browser compatibility** | Low | Medium | Use well-supported SVG features (feGaussianBlur, feColorMatrix), fallback to circles if not supported |
| **Framer Motion bundle size** | Medium | Low | Tree-shaking (import only used presets), consider lighter alternative if bundle >50KB |
| **Design token synchronization drift** | Low | Medium | Single source of truth (`design/tokens.ts`), CSS variables auto-generated, Tailwind extends tokens |
| **Reduced motion preference not respected** | Low | High | Test with `prefers-reduced-motion: reduce`, disable all animations when true |
| **Touch target violations** | Low | Medium | Voice button is 72px (well above 44px minimum), verify all interactive elements meet WCAG |
| **Color contrast issues** | Low | Medium | WCAG AA compliance verification during implementation, adjust token values if needed |
| **C007 delay blocks C008** | Medium | Low | C007 is on critical path, can implement token system independently while waiting |

---

## Open Questions

1. **Framer Motion version**: Should we pin a specific version (e.g., 10.16.4) or use `^` range?
   - **Recommendation**: Pin to exact version to avoid breaking changes
   - **Decision point**: During implementation (package.json setup)

2. **Metaball auto-disable threshold**: Is FPS <20 the right threshold for graceful degradation?
   - **Recommendation**: Start with FPS <20, adjust based on real device testing
   - **Decision point**: During implementation (performance monitoring setup)

3. **Mobile blob limit**: Is 6 blobs the right limit for mobile, or should it be 4?
   - **Recommendation**: Start with 6, reduce if performance issues arise
   - **Decision point**: During implementation (mobile testing)

4. **Color contrast verification**: Should we use automated tools (Axe, WAVE) or manual testing?
   - **Recommendation**: Both - automated tools for CI, manual testing for visual confirmation
   - **Decision point**: During implementation (testing phase)

---

**Next Artifact**: specs.md
