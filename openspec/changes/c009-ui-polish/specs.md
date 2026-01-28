# Specs Artifact: c009-ui-polish

**Generated**: 2026-01-29
**Change**: c009-ui-polish
**Schema**: spec-factory v1.0.0

---

## 1. Spec: visual-hierarchy

**File**: `specs/visual-hierarchy/spec.md`

**Purpose**: Define the visual hierarchy system that ensures clear information architecture with consistent sizing, spacing, and contrast ratios.

**Key Requirements**:
- All text uses token-based sizes (xs → voice)
- All colors use token-based colors (void → toast)
- All spacing uses token-based spacing (nucleus → ecosystem)
- WCAG AA compliance (contrast ratios)
- Consistent visual hierarchy across all components

**Acceptance Criteria**:
- [ ] All text uses token-based sizes
- [ ] All colors use token-based colors
- [ ] All spacing uses token-based spacing
- [ ] WCAG AA compliance verified

---

## 2. Spec: flat-design

**File**: `specs/flat-design/spec.md`

**Purpose**: Define the flat design system that removes gradients, uses subtle borders, and creates consistent visual surfaces.

**Key Requirements**:
- Headers use flat backgrounds (`bg-organelle`)
- Headers use subtle borders (`border-b border-white/[0.06]`)
- No gradients (`bg-gradient-to-*` prohibited)
- Surface layering follows void → membrane → cytoplasm → organelle
- Depth created via shadows, not gradients

**Acceptance Criteria**:
- [ ] All headers use flat backgrounds
- [ ] All headers use subtle borders
- [ ] No gradients found in codebase
- [ ] Surface layering consistent

---

## 3. Spec: single-accent

**File**: `specs/single-accent/spec.md`

**Purpose**: Define the single accent color system that standardizes all interactive elements to use one consistent accent color (enzyme/cyan).

**Key Requirements**:
- All interactive elements use `text-enzyme` or `bg-enzyme`
- Secondary elements use `text-ghost` (not green/gray/blue)
- Focus indicators use `ring-enzyme`
- Active states use enzyme variant (enzymeSoft, enzymeGlow)
- No mixed icon colors (all icons use enzyme or ghost)

**Acceptance Criteria**:
- [ ] All interactive elements use enzyme color
- [ ] All secondary elements use ghost color
- [ ] No mixed icon colors
- [ ] Focus indicators use enzyme ring

---

## 4. Spec: voice-interrupt

**File**: `specs/voice-interrupt/spec.md`

**Purpose**: Define the voice interrupt mechanism that provides a clear, obvious way for users to interrupt voice responses.

**Key Requirements**:
- Interrupt button spawns during audio playback
- Interrupt button uses interrupt animation (scale 0.8 → 1.1 → 1)
- Desktop: Space key interrupts voice playback
- Mobile: Tap button interrupts voice playback
- Touch target ≥44px
- ARIA label accurate ("Tap to interrupt" or "Press Space to interrupt")

**Acceptance Criteria**:
- [ ] Interrupt button spawns during audio playback
- [ ] Interrupt animation plays
- [ ] Space key interrupts on desktop
- [ ] Tap button interrupts on mobile
- [ ] Touch target ≥44px

---

## 5. Spec: spacing-tokens

**File**: `specs/spacing-tokens/spec.md`

**Purpose**: Ensure all spacing uses token-based values instead of arbitrary numbers for consistent layout.

**Key Requirements**:
- All padding uses spacing tokens (p-[nucleus] through p-[ecosystem])
- All margin uses spacing tokens (m-[nucleus] through m-[ecosystem])
- All gap uses spacing tokens (gap-[nucleus] through gap-[ecosystem])
- No arbitrary spacing values (p-4, m-6, gap-2 prohibited)

**Acceptance Criteria**:
- [ ] All padding uses spacing tokens
- [ ] All margin uses spacing tokens
- [ ] All gap uses spacing tokens
- [ ] No arbitrary spacing found

---

## 6. Cross-Domain Contracts

### 6.1 Shared Types

All C009 specs use existing C008 tokens:
- `tokens.color.*` (16 color values)
- `tokens.space.*` (7 spacing values)
- `tokens.font.*` (size, weight, leading)
- `tokens.layer.*` (8 z-index levels)
- `tokens.shadow.*` (5 shadow values)
- `motion.interrupt` (interrupt animation preset)

### 6.2 Integration Points

| Domain A | Domain B | Interface |
|----------|----------|-----------|
| **flat-design** | **visual-hierarchy** | Flat backgrounds use color hierarchy (void → organelle) |
| **single-accent** | **visual-hierarchy** | Accent color uses enzyme from color hierarchy |
| **spacing-tokens** | **visual-hierarchy** | Spacing tokens provide consistent layout |
| **voice-interrupt** | **C008 motion-presets** | Uses motion.interrupt preset |
| **voice-interrupt** | **C004 voice-streaming** | Interrupts audio playback |

### 6.3 Component Integration

All C009 refinements apply to existing C008 components:
- `VoiceButton` (voice-nucleus): Add interrupt button
- `Cell` (surfaces): Use flat backgrounds, subtle borders
- `Nucleus` (surfaces): Use single accent for focus state
- All widgets: Use token-based spacing and colors

---

**Next Artifact**: design.md
