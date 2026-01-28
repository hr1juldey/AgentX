# Design Artifact: c009-ui-polish

**Generated**: 2026-01-29
**Change**: c009-ui-polish
**Schema**: spec-factory v1.0.0

---

## 1. Architecture

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         UI Polish Architecture (C009)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Existing C008 Components (Refined)                │   │
│  │                                                                     │   │
│  │  ┌────────────────┐    ┌──────────────────┐    ┌──────────────┐   │   │
│  │  │ Design Tokens  │───▶│  Flat Design      │───▶│  Single      │   │   │
│  │  │  (from C008)   │    │  (No Gradients)   │    │  Accent      │   │   │
│  │  │                │    │                  │    │  (Enzyme)     │   │   │
│  │  └────────────────┘    └──────────────────┘    └──────────────┘   │   │
│  │                                                             │         │   │
│  │  ┌────────────────┐    ┌──────────────────┐    ┌──────────────┐   │   │
│  │  │ Spacing Tokens │───▶│  Voice Interrupt │───▶│  Visual      │   │   │
│  │  │  (from C008)   │    │  (Clear Button)   │    │  Hierarchy   │   │   │
│  │  │                │    │                  │    │              │   │   │
│  │  └────────────────┘    └──────────────────┘    └──────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    R014 Fixes (Before → After)                       │   │
│  │                                                                     │   │
│  │  Gradient Headers ──────────────▶ Flat Headers (bg-organelle)        │   │
│  │  Mixed Icons (green/blue/gray) ───▶ Single Accent (enzyme)           │   │
│  │  Low Contrast Text ─────────────▶ High Contrast (nucleus/protein)     │   │
│  │  Arbitrary Spacing (p-4, m-6) ────▶ Token Spacing (p-[tissue])       │   │
│  │  No Interrupt Button ───────────▶ Clear Interrupt (Google Assistant)  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Layer Structure (No Changes from C008)

C009 does not change the C008 layer structure. All refinements are applied to existing components:

```
frontend/
├── design/                 # (From C008, unchanged)
│   ├── tokens.ts           # Single source of truth
│   ├── motion.ts           # Motion presets
│   └── surfaces.tsx        # Primitive components (refined with flat design)
├── components/
│   ├── ui/
│   │   ├── voice-nucleus/  # (Refined with interrupt button)
│   │   ├── metaball/       # (Unchanged)
│   │   └── widgets/        # (Refined with token-based spacing)
│   └── agent/
│       ├── ui.tsx          # (Unchanged)
│       └── graph.ts        # (Unchanged)
└── styles/
    └── globals.css         # (Unchanged, CSS variables from C008)
```

---

## 2. Data Flow

### 2.1 Token Refinement Flow

```
C008 Design Tokens (Existing)
        │
        ├──▶ C009 Flat Design Refinement
        │       │
        │       ├──▶ Remove gradients
        │       ├──▶ Use flat backgrounds (bg-organelle)
        │       └──▶ Add subtle borders (border-b border-white/[0.06])
        │
        ├──▶ C009 Single Accent Refinement
        │       │
        │       ├──▶ Replace all icon colors with enzyme/ghost
        │       └──▶ Update focus indicators (ring-enzyme)
        │
        ├──▶ C009 Spacing Token Refinement
        │       │
        │       ├──▶ Replace arbitrary spacing with tokens
        │       └──▶ Verify consistent layout
        │
        └──▶ C009 Voice Interrupt Addition
                │
                ├──▶ Add interrupt button component
                ├──▶ Wire interrupt animation (motion.interrupt)
                └──▶ Test on desktop (Space) and mobile (tap)
```

### 2.2 Grep Find/Replace Flow

```
1. Remove Gradients:
   grep -r "bg-gradient-to-" frontend/
   Replace with: "bg-organelle border-b border-white/[0.06]"

2. Standardize Icon Colors:
   grep -r "text-green-\|text-blue-\|text-gray-" frontend/
   Replace with: "text-enzyme" (primary) or "text-ghost" (secondary)

3. Token-Based Spacing:
   grep -r "p-[0-9]\|m-[0-9]\|gap-[0-9]" frontend/
   Replace with: "p-[tissue]", "m-[organ]", "gap-[cell]" etc.

4. Verify No Regressions:
   - Run visual inspection
   - Run Axe DevTools audit
   - Test on real devices
```

---

## 3. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| **Gradient Removal** | Remove all gradients | Keep some gradients | Raycast minimalism reference, consistent with modern design |
| **Single Accent** | Enzyme/cyan for all interactive elements | Multiple accents | Consistent visual language, easier to understand |
| **Token-Based Spacing** | Use C008 spacing tokens | Add more tokens | C008 tokens comprehensive, DRY principle |
| **Interrupt Button** | Fixed bottom-center (mobile), floating top-right (desktop) | No interrupt button | Google Assistant clarity, obvious interrupt mechanism |
| **Grep Find/Replace** | Automated find/replace | Manual changes | Simple, reliable, automatable |
| **No New Tokens** | Use existing C008 tokens | Add new tokens | C008 already comprehensive, no new tokens needed |

---

## 4. Tradeoff Analysis

### 4.1 Approach A: Remove All Gradients (CHOSEN)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐⭐ | Simple grep find/replace |
| Performance | ⭐⭐⭐ | No performance impact (CSS only) |
| Consistency | ⭐⭐⭐ | Consistent with Raycast minimalism |
| Visual Impact | ⭐⭐⭐ | Cleaner, more professional look |

**Pros**:
- Consistent with Raycast minimalism
- Removes visual noise
- Simpler design system
- More professional look

**Cons**:
- None significant (gradients don't add value)

### 4.2 Approach B: Keep Some Gradients

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐ | More complex design rules |
| Performance | ⭐⭐⭐ | No performance impact |
| Consistency | ⭐ | Inconsistent design language |
| Visual Impact | ⭐⭐ | Dated look (gradients are 2010s trend) |

**Pros**:
- None (gradients are dated)

**Cons**:
- Inconsistent design language
- Visual noise
- Dated look

### 4.3 Decision: Remove All Gradients

**Rationale**:
- **Raycast minimalism** is the reference standard
- **Modern design** has moved away from gradients
- **Consistency** is more important than variety
- **Professional look** is cleaner without gradients

---

## 5. Implementation Details

### 5.1 Key Classes/Modules

| Module | Responsibility | Changes |
|--------|----------------|----------|
| **design/tokens.ts** | Single source of truth | No changes (use existing tokens) |
| **design/motion.ts** | Motion presets | No changes (use motion.interrupt) |
| **design/surfaces.tsx** | Primitive components | Refine Cell component (flat background, subtle border) |
| **components/ui/voice-nucleus/VoiceButton.tsx** | Voice button | Add interrupt button, Space key handling |
| **components/ui/widgets/** | Widget components | Refine spacing (token-based), colors (single accent) |

### 5.2 Port Assignments

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| **Frontend (Next.js)** | 3000 | HTTP | Main frontend application (from C007) |

**Note**: C009 uses existing ports from C007. No new ports required.

### 5.3 File Structure (Implementation Changes)

```
frontend/
├── components/
│   ├── ui/
│   │   ├── voice-nucleus/
│   │   │   ├── VoiceButton.tsx       # CHANGED: Add interrupt button
│   │   │   └── Nucleus.tsx           # CHANGED: Flat background, subtle border
│   │   └── widgets/                  # CHANGED: Token-based spacing, single accent
│   │       ├── MarkdownWidget.tsx    # Refine spacing/colors
│   │       ├── CardWidget.tsx        # Refine spacing/colors
│   │       └── ...
│   └── agent/
│       ├── ui.tsx                    # UNCHANGED
│       └── graph.ts                  # UNCHANGED
└── scripts/
    └── polish-cs109.ts               # NEW: Grep find/replace script
```

---

## 6. Security Considerations

| Concern | Mitigation |
|---------|------------|
| **No security concerns** | C009 is frontend-only UI polish with no security implications |

**Note**: C009 is a frontend UI polish change with minimal security concerns. Main security is handled by C007 (LangGraph server-driven UI) and C004 (voice WebSocket).

---

## 7. Performance Considerations

| Concern | Mitigation |
|---------|------------|
| **CSS Changes** | No performance impact (CSS only, flat backgrounds faster than gradients) |
| **Token Access** | No performance impact (tokens are frozen constants) |
| **Interrupt Button** | Minimal DOM impact (single button component, <50 lines) |
| **Grep Find/Replace** | One-time cost during implementation, no runtime impact |

**Performance Targets**:
- No performance regression (all changes are CSS/visual only)
- Bundle size: No increase (no new dependencies)
- Runtime: No change (flat backgrounds faster than gradients)

---

## 8. Accessibility Considerations

| Concern | Mitigation |
|---------|------------|
| **WCAG AA Compliance** | Use C008 tokens (already designed for WCAG AA) |
| **Color Contrast** | Verify with Axe DevTools (nucleus 96%, protein 72% pass) |
| **Touch Targets** | Interrupt button ≥44px (complies with WCAG) |
| **Keyboard Accessibility** | Space key for interrupt, clear focus indicators |
| **Screen Reader** | ARIA labels for interrupt button |

**WCAG 2.1 AA Compliance**:
- Color contrast: ≥4.5:1 for normal text, ≥3:1 for large text (C008 tokens satisfy)
- Touch targets: ≥44x44px (interrupt button satisfies)
- Keyboard accessibility: Full keyboard support (Space key, focus indicators)
- Screen reader: Semantic HTML, ARIA labels

---

**Next Artifact**: tasks.md
