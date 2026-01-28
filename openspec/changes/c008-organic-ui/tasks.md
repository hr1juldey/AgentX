# Tasks Artifact: c008-organic-ui

**Generated**: 2026-01-29
**Change**: c008-organic-ui
**Schema**: spec-factory v1.0.0

---

## 1. Implementation Checklist

### 1.1 Phase 1: Design Token System (Day 1)

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create design directory | `frontend/design/` | ⬜ | `mkdir -p design` |
| Create tokens.ts | `design/tokens.ts` | ⬜ | All 11 token categories, ~180 lines |
| Create motion.ts | `design/motion.ts` | ⬜ | 9 presets + stagger, ~150 lines |
| Generate CSS variables | `styles/globals.css` | ⬜ | Auto-generated from tokens.ts |
| Extend Tailwind config | `tailwind.config.js` | ⬜ | Extend tokens (no duplication) |
| Install Framer Motion | `package.json` | ⬜ | `npm install framer-motion` |
| Verify token access | TypeScript check | ⬜ | `tokens.color.void` should compile |

### 1.2 Phase 2: Primitive Components (Day 1)

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create surfaces.tsx | `design/surfaces.tsx` | ⬜ | Or split into Cell.tsx, Nucleus.tsx, StreamText.tsx |
| Implement Cell component | `design/surfaces.tsx` or `Cell.tsx` | ⬜ | Glass surface, <60 lines |
| Implement Nucleus component | `design/surfaces.tsx` or `Nucleus.tsx` | ⬜ | Circular container, <80 lines |
| Implement StreamText component | `design/surfaces.tsx` or `StreamText.tsx` | ⬜ | Text streaming animation, <40 lines |
| Test primitive components | Storybook/Dev mode | ⬜ | Visual inspection |

### 1.3 Phase 3: Voice Nucleus (Day 2)

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create voice-nucleus directory | `components/ui/voice-nucleus/` | ⬜ | `mkdir -p components/ui/voice-nucleus` |
| Implement VoiceButton | `VoiceButton.tsx` | ⬜ | Platform-aware sizing, <100 lines |
| Add keyboard support | `VoiceButton.tsx` | ⬜ | Space key toggle |
| Add screen reader support | `VoiceButton.tsx` | ⬜ | ARIA labels, pressed state |
| Test on desktop | Browser (desktop) | ⬜ | 160px size, center position |
| Test on mobile | Browser (mobile) | ⬜ | 72px size, bottom-center position |
| Test reduced motion | Browser (prefers-reduced-motion) | ⬜ | Animations disabled |

### 1.4 Phase 4: Metaball System (Day 2-3)

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create metaball directory | `components/ui/metaball/` | ⬜ | `mkdir -p components/ui/metaball` |
| Implement SVG goo filter | `MetaballCanvas.tsx` | ⬜ | Platform-aware blur, <100 lines |
| Implement physics engine | `physics.ts` | ⬜ | Spring physics, <80 lines |
| Add performance monitoring | `MetaballCanvas.tsx` | ⬜ | FPS counter, auto-disable at FPS <20 |
| Test on desktop | Browser (desktop) | ⬜ | 16px blur, 12 blobs, ≥60fps |
| Test on mobile | Browser (mobile) | ⬜ | 12px blur, 6 blobs, ≥30fps |
| Test graceful degradation | Browser (throttled CPU) | ⬜ | Auto-disable, fallback to circles |

### 1.5 Phase 5: Integration (Day 3)

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create agent directory | `components/agent/` | ⬜ | `mkdir -p components/agent` |
| Create widget registry | `ui.tsx` | ⬜ | Colocated with graph.py, ~50 lines |
| Integrate with LangGraph | `components/agent/` | ⬜ | Use `useStream()`, `LoadExternalComponent` |
| Test widget spawning | Browser | ⬜ | Mitosis animation, metaball merging |
| Test platform adaptation | Browser (desktop + mobile) | ⬜ | Correct sizing and blur |
| Test accessibility | Axe DevTools, keyboard, screen reader | ⬜ | WCAG AA compliance |

### 1.6 Phase 6: Polish (Day 4)

| Task | File | Status | Notes |
|------|------|--------|-------|
| Verify all token references | Grep check | ⬜ | No hardcoded colors/spacings |
| Verify CSS variables | `globals.css` | ⬜ | All tokens present |
| Verify Tailwind extension | `tailwind.config.js` | ⬜ | All tokens extended |
| Run accessibility audit | Axe DevTools | ⬜ | Zero critical issues |
| Run performance audit | Lighthouse | ⬜ | Score ≥90 |
| Test on real devices | Desktop, tablet, mobile | ⬜ | Visual inspection |

---

## 2. Verification Steps

### 2.1 Code Quality (Frontend)

```bash
# Type check
npx tsc --noEmit

# Lint (ESLint)
npm run lint

# Format (Prettier)
npm run format

# Bundle size check
npm run build
# Verify bundle size <50KB (gzipped) for design system
```

### 2.2 File Size Check

```bash
# Verify no file exceeds 100 lines (executable)
find frontend/design frontend/components/ui -name "*.ts" -o -name "*.tsx" | xargs wc -l | awk '$1 > 100'

# Verify tokens.ts under 200 lines (acceptable for config file)
wc -l frontend/design/tokens.ts
```

### 2.3 Import Check

```bash
# Verify absolute imports only (no relative imports)
grep -r "from '\./" frontend/design frontend/components/ui  # Should return nothing
grep -r 'from "\./' frontend/design frontend/components/ui  # Should return nothing
```

### 2.4 Token Coverage Check

```bash
# Verify all UI elements reference tokens (no hardcoded values)
grep -r "#[0-9A-Fa-f]\{6\}" frontend/design frontend/components/ui | grep -v "tokens.ts" | grep -v "globals.css"
# Should return nothing (no hardcoded hex colors)

grep -r "[0-9]\+px" frontend/design frontend/components/ui | grep -v "tokens.ts" | grep -v "globals.css"
# Should return nothing (no hardcoded pixel values)
```

---

## 3. Acceptance Criteria

### 3.1 Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| Design tokens defined | Inspect `design/tokens.ts` | All 11 token categories present |
| CSS variables generated | Inspect `styles/globals.css` | All tokens present as CSS variables |
| Tailwind extends tokens | Inspect `tailwind.config.js` | All tokens extended (no duplication) |
| Platform-aware metaballs | Test on desktop + mobile | Desktop: 16px blur, 12 blobs; Mobile: 12px blur, 6 blobs |
| Voice nucleus sizing | Test on desktop + mobile | Desktop: 160px; Mobile: 72px |
| Pulse animation | Activate voice state | Scale 1.08, glow → pulse → glow |
| Drift animation | Idle state | y: -8→0→8, x: 0→4→0 |
| Keyboard accessibility | Tab + Space key | Voice nucleus focused, state toggles |
| Screen reader support | Screen reader (NVDA/VoiceOver) | ARIA labels accurate |
| Reduced motion | `prefers-reduced-motion: reduce` | All animations disabled |
| Auto-disable | Throttle CPU (4x slowdown) | Metaballs disable when FPS <20 |
| Graceful degradation | Inspect disabled state | Falls back to clean circles |

### 3.2 Non-Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| Desktop performance | FPS monitor (12 blobs) | ≥60fps |
| Mobile performance | FPS monitor (6 blobs) | ≥30fps |
| Bundle size | Build + gzip | <50KB (gzipped) for design system |
| Token coverage | Grep check | 100% token coverage (no hardcoded values) |
| File size limits | WC check | All files <100 lines (tokens.ts <200) |
| Import rules | Grep check | 0 relative imports |
| Type safety | TypeScript check | 0 type errors |
| Accessibility | Axe DevTools audit | 0 critical issues |
| Visual consistency | Visual inspection | Biological metaphor applied consistently |

---

## 4. Definition of Done

C008-organic-ui is **complete** when:

- [ ] All 6 phases are implemented (Foundation, Primitives, Voice Nucleus, Metaballs, Integration, Polish)
- [ ] All verification steps pass (code quality, file size, imports, token coverage)
- [ ] All functional acceptance criteria are met (12 criteria)
- [ ] All non-functional acceptance criteria are met (9 criteria)
- [ ] Design tokens match LLD exactly (line-by-line verification)
- [ ] Platform-aware performance targets met (desktop ≥60fps, mobile ≥30fps)
- [ ] WCAG AA compliance verified (0 critical accessibility issues)
- [ ] Visual inspection passes on desktop, tablet, and mobile
- [ ] Code review approved
- [ ] Documentation updated (if applicable)

---

## 5. Rollback Plan

If implementation fails:

1. **Identify failure point**:
   - Performance issue: Check FPS monitor, blob count, blur radius
   - Visual issue: Inspect CSS variables, Tailwind config
   - Integration issue: Check LangGraph connection, widget registry
   - Accessibility issue: Run Axe DevTools audit

2. **Rollback steps**:
   ```bash
   # Rollback to previous working state
   git checkout HEAD~1 frontend/design frontend/components/ui

   # Or revert specific files
   git checkout HEAD~1 -- frontend/design/tokens.ts
   git checkout HEAD~1 -- frontend/design/motion.ts
   ```

3. **Recovery actions**:
   - Performance: Reduce blob count (6→4 on mobile), reduce blur (12px→8px), disable metaballs entirely
   - Visual: Revert CSS variables, re-run Tailwind build, clear browser cache
   - Integration: Re-check C007 LangGraph setup, verify widget registry format
   - Accessibility: Fix ARIA labels, add missing focus states, increase touch targets

---

## 6. Dependencies Unlocked

This change unlocks:

| Change | Unlocked Feature |
|--------|-----------------|
| **C009-ui-polish** | UI polish layer (Raycast minimalism, Google Assistant clarity, aesthetic fixes) |

---

## 7. Implementation Notes

### 7.1 C007 Dependency

C008 depends on C007 (frontend-architecture) for:
- LangGraph server-driven UI pattern (`push_ui_message()`, `LoadExternalComponent`)
- Widget registry format (`ui.tsx` colocated with `graph.py`)
- Component colocation strategy

**If C007 is not complete**:
- Implement token system independently (Phase 1-2 can proceed)
- Defer integration (Phase 5) until C007 is complete
- Use mock widget data for testing

### 7.2 C003 Dependency

C008 depends on C003 (agent-pipeline) for:
- LangGraph state management with `ui_message_reducer`
- Backend graph execution

**If C003 is not complete**:
- Implement visual layer independently (Phase 1-4 can proceed)
- Defer integration (Phase 5) until C003 is complete
- Use mock widget messages for testing

### 7.3 C004 Dependency

C008 consumes C004 (voice-streaming) for:
- Voice WebSocket connection
- Audio streaming

**If C004 is not complete**:
- Implement voice nucleus visuals independently
- Defer WebSocket integration until C004 is complete
- Use mock audio state for testing

---

**End of spec-factory pipeline**

All 7 artifacts complete for C008-organic-ui:
1. ✅ scan.md
2. ✅ extract.md
3. ✅ validate.md
4. ✅ proposal.md
5. ✅ specs.md (with 4 spec files)
6. ✅ design.md
7. ✅ tasks.md
