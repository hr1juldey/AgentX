# Tasks Artifact: c009-ui-polish

**Generated**: 2026-01-29
**Change**: c009-ui-polish
**Schema**: spec-factory v1.0.0

---

## 1. Implementation Checklist

### 1.1 Phase 1: Visual Hierarchy (1 hour)

| Task | Command/File | Status | Notes |
|------|-------------|--------|-------|
| Audit text sizes | Grep all `font-size`, `text-*` classes | ⬜ | Find all non-token text sizes |
| Replace with token-based sizes | Grep replace | ⬜ | Use `text-xs` through `text-voice` |
| Audit colors | Grep all hex codes, `text-*` colors | ⬜ | Find all non-token colors |
| Replace with token-based colors | Grep replace | ⬜ | Use `text-nucleus`, `text-protein`, `text-ghost`, `text-enzyme` |
| Audit spacing | Grep all `p-*`, `m-*`, `gap-*` with numbers | ⬜ | Find all arbitrary spacing |
| Replace with token-based spacing | Grep replace | ⬜ | Use `p-[nucleus]` through `p-[ecosystem]` |
| Verify WCAG AA compliance | Axe DevTools audit | ⬜ | Zero contrast issues |

### 1.2 Phase 2: Flat Design (30 minutes)

| Task | Command/File | Status | Notes |
|------|-------------|--------|-------|
| Find all gradients | `grep -r "bg-gradient-to-" frontend/` | ⬜ | List all gradient backgrounds |
| Replace with flat backgrounds | Grep replace | ⬜ | `bg-organelle border-b border-white/[0.06]` |
| Verify no gradients remain | `grep -r "bg-gradient-to-" frontend/` | ⬜ | Should return 0 matches |
| Verify surface layering | Visual inspection | ⬜ | void → membrane → cytoplasm → organelle |

### 1.3 Phase 3: Single Accent (30 minutes)

| Task | Command/File | Status | Notes |
|------|-------------|--------|-------|
| Find mixed icon colors | `grep -r "text-green-\|text-blue-\|text-gray-" frontend/` | ⬜ | List all non-enzyme icon colors |
| Replace with enzyme | Grep replace | ⬜ | Primary: `text-enzyme`, Secondary: `text-ghost` |
| Update focus indicators | Grep replace | ⬜ | `ring-enzyme` |
| Verify no mixed colors | `grep -r "text-green-\|text-blue-\|text-gray-" frontend/` | ⬜ | Should return 0 matches |

### 1.4 Phase 4: Spacing Tokens (30 minutes)

| Task | Command/File | Status | Notes |
|------|-------------|--------|-------|
| Find arbitrary padding | `grep -r "p-[0-9]" frontend/` | ⬜ | List all arbitrary padding |
| Replace with tokens | Grep replace | ⬜ | Map to nearest token (4→nucleus, 8→cell, 16→tissue, etc.) |
| Find arbitrary margin | `grep -r "m-[0-9]" frontend/` | ⬜ | List all arbitrary margin |
| Replace with tokens | Grep replace | ⬜ | Map to nearest token |
| Find arbitrary gap | `grep -r "gap-[0-9]" frontend/` | ⬜ | List all arbitrary gap |
| Replace with tokens | Grep replace | ⬜ | Map to nearest token |
| Verify token coverage | `grep -r "p-[0-9]\|m-[0-9]\|gap-[0-9]" frontend/` | ⬜ | Should return 0 matches |

### 1.5 Phase 5: Voice Interrupt (30 minutes)

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create interrupt button component | `components/ui/voice-nucleus/InterruptButton.tsx` | ⬜ | <50 lines, use motion.interrupt |
| Wire Space key handling | `VoiceButton.tsx` | ⬜ | Desktop interrupt |
| Wire tap handling | `InterruptButton.tsx` | ⬜ | Mobile interrupt |
| Add ARIA labels | `InterruptButton.tsx` | ⬜ | "Tap to interrupt" / "Press Space to interrupt" |
| Test interrupt on desktop | Browser | ⬜ | Space key works |
| Test interrupt on mobile | Browser | ⬜ | Tap button works |
| Verify touch target | Visual inspection | ⬜ | ≥44px |

### 1.6 Phase 6: Verification (30 minutes)

| Task | Method | Status | Notes |
|------|--------|--------|-------|
| Verify no gradients | Grep check | ✓ | 0 matches (2026-01-31) |
| Verify single accent | Grep check | ✓ | 0 matches (2026-01-31) |
| Verify token spacing | Grep check | ✓ | 0 matches (2026-01-31) |
| Run accessibility audit | Axe DevTools | ⬜ | Zero critical issues (pending manual audit) |
| Run visual inspection | Manual (desktop, tablet, mobile) | ⬜ | Consistent visual language (pending visual verification) |

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
```

### 2.2 Grep Validation Commands

```bash
# Verify no gradients
grep -r "bg-gradient-to-" frontend/
# Expected: 0 matches

# Verify no mixed icon colors
grep -r "text-green-\|text-blue-\|text-gray-" frontend/
# Expected: 0 matches

# Verify token-based spacing
grep -r "p-[0-9]\|m-[0-9]\|gap-[0-9]" frontend/ | grep -v "p-\["
# Expected: 0 matches (all spacing should use p-[token-name] format)
```

### 2.3 Accessibility Audit

```bash
# Run Axe DevTools audit
# (Manual: Open DevTools → Axe DevTools → Scan page)
# Expected: Zero critical issues, WCAG AA pass
```

---

## 3. Acceptance Criteria

### 3.1 Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| No gradients | Grep check | 0 matches for `bg-gradient-to-*` |
| Single accent | Grep check | 0 matches for mixed icon colors |
| Token spacing | Grep check | 0 matches for arbitrary spacing |
| WCAG AA compliance | Axe DevTools audit | Zero contrast issues |
| Voice interrupt works | Manual test | Space/tap interrupts audio |
| Visual consistency | Visual inspection | All components follow same visual language |

### 3.2 Non-Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| No performance regression | Lighthouse audit | Score ≥90 (same as C008) |
| Bundle size | Build + gzip | No increase (C008 bundle unchanged) |
| Type safety | TypeScript check | 0 type errors |
| Accessibility | Axe DevTools audit | 0 critical issues |

---

## 4. Definition of Done

C009-ui-polish is **complete** when:

- [x] All grep verification checks pass (no gradients, single accent, token spacing)
- [ ] Manual accessibility audit (Axe DevTools) - Zero critical issues
- [ ] Visual inspection on desktop, tablet, and mobile
- [ ] Voice interrupt button implementation (Phase 5)
- [ ] Code review approved
- [ ] Documentation updated (if applicable)

**Status**: Automated verification complete (2026-01-31)
- ✅ No gradients found (0 matches)
- ✅ Single accent verified (0 mixed colors)
- ✅ Token spacing verified (0 arbitrary spacing)

**Remaining** (manual tasks):
- ⬜ Accessibility audit with Axe DevTools
- ⬜ Visual inspection on real devices
- ⬜ Voice interrupt button implementation (Phase 5)

---

## 5. Rollback Plan

If implementation fails:

1. **Identify failure point**:
   - Visual issue: Revert CSS changes, check spacing tokens
   - Accessibility issue: Revert color changes, use C008 defaults
   - Interrupt issue: Revert interrupt button, use C008 voice nucleus only

2. **Rollback steps**:
   ```bash
   # Rollback CSS changes
   git checkout HEAD~1 frontend/components/ui
   git checkout HEAD~1 frontend/styles
   ```

3. **Recovery actions**:
   - Visual: Re-apply grep replacements with corrected patterns
   - Accessibility: Use C008 token defaults (already WCAG AA compliant)
   - Interrupt: Simplify interrupt button (remove animation, keep functionality)

---

## 6. Dependencies Unlocked

This change unlocks:

| Change | Unlocked Feature |
|--------|-----------------|
| **C006-release-plan** | Phase 10: Hardening (Tests, Errors, Monitoring) |

**Note**: C009 is the final frontend phase. After C009 completion, the system moves to Phase 10 (Hardening).

---

## 7. Implementation Notes

### 7.1 C008 Dependency

C009 depends on C008 (organic-ui) for:
- Design tokens (color, space, font, radius, shadow, layer)
- Motion presets (interrupt animation)
- Primitive components (Cell, Nucleus, StreamText)

**If C008 is not complete**:
- Defer C009 until C008 is complete
- Use mock token data for testing

### 7.2 Grep Find/Replace Strategy

**Automated Script**:
```bash
#!/bin/bash
# polish-c009.sh

# Phase 1: Remove gradients
find frontend/ -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.css" \) -exec sed -i 's/bg-gradient-to-r from-void to-membrane/bg-organelle border-b border-white\/[0.06]/g' {} +

# Phase 2: Single accent
find frontend/ -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i 's/text-green-500/text-enzyme/g' {} +
find frontend/ -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i 's/text-blue-500/text-enzyme/g' {} +
find frontend/ -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i 's/text-gray-400/text-ghost/g' {} +

# Phase 3: Spacing tokens (example)
find frontend/ -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i 's/p-4/p-[tissue]/g' {} +
find frontend/ -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i 's/m-6/m-[organ]/g' {} +
```

**Manual Review Required**:
- Visual inspection after each phase
- Accessibility audit after all phases
- Test on real devices (desktop, tablet, mobile)

---

## 8. Success Metrics

### 8.1 Quantitative Metrics

| Metric | Before (R014) | After (C009) | Target |
|--------|---------------|--------------|--------|
| Gradient backgrounds | 5+ | 0 | 0 |
| Mixed icon colors | 10+ | 0 | 0 |
| Arbitrary spacing | 50+ | 0 | 0 |
| WCAG AA issues | 3+ | 0 | 0 |
| Voice interrupt mechanism | None | Clear button | ✅ |

### 8.2 Qualitative Metrics

| Metric | Before (R014) | After (C009) |
|--------|---------------|--------------|
| Visual consistency | Low (mixed styles) | High (consistent tokens) |
| Professional polish | Medium | High (Raycast minimalism) |
| Accessibility | Medium (some issues) | High (WCAG AA compliant) |
| Voice clarity | Low (no clear interrupt) | High (Google Assistant pattern) |

---

**End of spec-factory pipeline**

All 7 artifacts complete for C009-ui-polish:
1. ✅ scan.md
2. ✅ extract.md
3. ✅ validate.md
4. ✅ proposal.md
5. ✅ specs.md (with 5 spec files)
6. ✅ design.md
7. ✅ tasks.md
