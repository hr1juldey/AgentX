# Proposal: c009-ui-polish

**Generated**: 2026-01-29
**Change**: c009-ui-polish
**Schema**: spec-factory v1.0.0

---

## Summary

Implement the UI polish layer for AgentX v0.1, applying Raycast minimalism and Google Assistant voice clarity patterns to refine the visual aesthetics. This change focuses on removing gradients, standardizing icon colors to a single accent, improving contrast ratios, using token-based spacing, and adding a clear voice interrupt mechanism.

---

## Motivation

### Problem Statement

R014 UI showcase has several aesthetic issues that impact professional polish:
1. **Gradient headers** create visual noise and inconsistent design language
2. **Mixed icon colors** (green/gray/blue) create inconsistent visual hierarchy
3. **Poor dev console contrast** fails WCAG AA accessibility standards
4. **Arbitrary spacing** (p-4, m-6, gap-2) creates inconsistent layout
5. **No clear voice interrupt mechanism** makes it hard to stop AI responses

### Current State

R014 UI showcase provides:
- Gradient headers (visual noise, inconsistent with flat design)
- Mixed icon colors (green for success, gray for disabled, blue for info)
- Low contrast text (fails WCAG AA)
- Arbitrary spacing values (4px, 8px, 16px mixed inconsistently)
- No dedicated interrupt button (users must figure out how to stop voice)

### Desired State

C009 UI Polish delivers:
- **Flat headers** (Raycast minimalism, subtle borders)
- **Single accent color** (enzyme/cyan for all interactive elements)
- **High contrast text** (WCAG AA compliant, using C008 tokens)
- **Token-based spacing** (consistent layout using C008 spacing tokens)
- **Voice interrupt button** (Google Assistant clarity, clear tap/space to interrupt)

---

## Scope

### In Scope

- **Visual hierarchy**: Text sizes, colors, spacing, z-index layers (use existing C008 tokens)
- **Flat design**: Remove gradients, use subtle borders, flat backgrounds
- **Single accent**: Standardize all interactive elements to use enzyme/cyan color
- **Spacing tokens**: Replace arbitrary spacing with token-based spacing (nucleus → ecosystem)
- **Voice interrupt**: Add clear interrupt mechanism with interrupt animation
- **Accessibility**: WCAG AA compliance (contrast ratios, touch targets, ARIA labels)
- **Consistency**: Ensure all components follow same visual language

### Out of Scope

- **New components**: No new components created (only refinements to existing C008 components)
- **New tokens**: All refinements use existing C008 tokens (no new design tokens needed)
- **Layout system**: Widget anchors and mobile stack deferred to implementation phase
- **Motion animations**: Uses existing C008 motion presets (no new animations)
- **Backend changes**: Frontend-only, no backend API changes

### Dependencies

| Change | Status | Required For |
|--------|--------|--------------|
| **C008-organic-ui** | Pending | Design tokens (color, space, font, radius, shadow, layer) |
| **C007-frontend-architecture** | Pending | LangGraph server-driven UI pattern |
| **C003-agent-pipeline** | Done | LangGraph state management |
| **C004-voice-streaming** | Done | Voice WebSocket for audio playback/interrupt |

---

## Success Criteria

1. **No Gradients**: All gradient backgrounds removed, replaced with flat backgrounds
   - Measure: Grep check for `bg-gradient-to-*` returns 0 matches
   - Target: 0 gradient backgrounds

2. **Single Accent**: All interactive elements use enzyme color
   - Measure: Grep check for mixed icon colors (green-*, blue-*, gray-*) returns 0 matches
   - Target: 0 mixed icon colors

3. **WCAG AA Compliance**: All text meets contrast requirements
   - Measure: Axe DevTools audit, automated contrast check
   - Target: Zero contrast issues, WCAG AA pass

4. **Token-Based Spacing**: All spacing uses tokens
   - Measure: Grep check for arbitrary spacing (p-*, m-*, gap-* where * is number) returns 0 matches
   - Target: 100% token-based spacing

5. **Voice Interrupt**: Clear interrupt mechanism available
   - Measure: Manual test (desktop: Space, mobile: tap button)
   - Target: Interrupt button spawns during audio playback, works correctly

6. **Visual Consistency**: All components follow same visual language
   - Measure: Visual inspection across all components
   - Target: Consistent colors, spacing, sizing, borders

---

## Implementation Approach

### High-Level Approach

**Phase 1: Visual Hierarchy** (1 hour)
- Audit all text sizes, colors, spacing
- Replace with C008 tokens (font.size, color, space)
- Verify WCAG AA compliance

**Phase 2: Flat Design** (30 minutes)
- Remove all gradient backgrounds
- Replace with flat backgrounds + subtle borders
- Update headers, cards, surfaces

**Phase 3: Single Accent** (30 minutes)
- Replace all icon colors with enzyme/ghost
- Update interactive elements (buttons, links)
- Standardize focus indicators (ring-enzyme)

**Phase 4: Spacing Tokens** (30 minutes)
- Replace arbitrary spacing with tokens
- Update padding, margin, gap
- Verify consistent layout

**Phase 5: Voice Interrupt** (30 minutes)
- Add interrupt button component
- Wire interrupt animation
- Test on desktop (Space) and mobile (tap)

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| **No new tokens** | C008 tokens already comprehensive (color, space, font, radius, shadow, layer) | Add more tokens (unnecessary complexity) |
| **Flat over gradients** | Raycast minimalism reference, consistent with modern design trends | Keep gradients (dated, visual noise) |
| **Single accent color** | Consistent visual language, easier to understand | Multiple accents (confusing, inconsistent) |
| **Token-based spacing** | Consistent layout, DRY principle | Arbitrary spacing (inconsistent, harder to maintain) |
| **Google Assistant interrupt** | Clear, obvious, follows established pattern | No interrupt button (users can't stop voice) |
| **Grep find/replace** | Simple, reliable, automatable | Manual changes (error-prone, slow) |

### Constraints

- **Ports**: No new ports (uses frontend port 3000 from C007)
- **File size**: No new files created (only modifications to existing C008 components)
- **Imports**: Absolute imports only (`@/design/tokens`)
- **Dependencies**: Must wait for C008 completion (design tokens required)
- **Browser support**: Modern browsers only (Chrome 90+, Safari 14+, Firefox 88+, Edge 90+)

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **C008 delay blocks C009** | Medium | Low | C008 is on critical path, but C009 is final polish phase (can be deferred if needed) |
| **Grep find/replace errors** | Low | Medium | Use dry-run mode first, verify all replacements, manual review |
| **WCAG AA compliance issues** | Low | Low | C008 tokens already designed for WCAG AA (nucleus 96%, protein 72%) |
| **Voice interrupt complexity** | Low | Medium | Use existing C008 motion.interrupt preset, simple button component |
| **Inconsistent spacing after token migration** | Low | Medium | Test all components after migration, adjust tokens if needed |

---

## Open Questions

1. **Voice interrupt placement**: Should interrupt button be floating (top-right) or fixed (bottom-center)?
   - **Recommendation**: Fixed bottom-center on mobile (thumb-friendly), floating top-right on desktop
   - **Decision point**: During implementation (visual testing)

2. **Spacing token granularity**: Are 7 tokens enough (nucleus, cell, tissue, organ, organism, colony, ecosystem)?
   - **Recommendation**: Start with 7 tokens, add more only if needed (7 sufficient for most use cases)
   - **Decision point**: During implementation (testing)

3. **Gradient removal scope**: Should we remove all gradients or keep some for special cases (e.g., voice pulse)?
   - **Recommendation**: Remove all static gradients (headers, cards), keep dynamic animations (pulse already uses shadow animation, not gradient)
   - **Decision point**: During implementation (code review)

---

**Next Artifact**: specs.md
