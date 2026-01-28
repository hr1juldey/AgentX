# Extract Artifact: c009-ui-polish

**Generated**: 2026-01-29
**Change**: c009-ui-polish
**Schema**: spec-factory v1.0.0

---

## 1. Pattern Catalog

### 1.1 Architectural Patterns

| Pattern | Source | Description | Apply? |
|---------|--------|-------------|--------|
| **Raycast Minimalism** | Raycast app (reference) | Flat design, consistent spacing, single accent, monochrome base | ✅ |
| **Google Assistant Voice Clarity** | Google Assistant (reference) | Clear visual hierarchy, obvious interrupt mechanism, minimal chrome | ✅ |
| **Token-Based Design System** | C008 Organic UI | All aesthetics use existing tokens (no new tokens needed) | ✅ |
| **Flat Headers** | Plan exploration (R014 fix) | Remove gradients, use flat backgrounds with subtle borders | ✅ |
| **Single Accent Color** | Plan exploration (R014 fix) | Standardize to one accent color (enzyme/cyan) for all interactive elements | ✅ |
| **High Contrast Text** | WCAG AA compliance | Use token-based text colors (nucleus 96%, protein 72%, ghost 38%) | ✅ |
| **Consistent Spacing** | C008 tokens | Use spacing tokens instead of arbitrary values | ✅ |

### 1.2 Code Structure Patterns

| Pattern | Example | Apply? |
|---------|---------|--------|
| **Flat Header Pattern** | `className="bg-organelle border-b"` | ✅ |
| **Single Accent Icon Pattern** | `className="text-enzyme"` | ✅ |
| **Spacing Token Pattern** | `className="p-[tissue]"` | ✅ |
| **High Contrast Text Pattern** | `className="text-protein"` | ✅ |
| **Voice Interrupt Button** | Dedicated button with interrupt animation | ✅ |
| **Minimal Chrome Pattern** | Focus on content, not UI | ✅ |

### 1.3 Naming Patterns (to Avoid from R014)

| R014 Name | Why Avoid | Alternative |
|-----------|-----------|-------------|
| `bg-gradient-to-r` | Gradients create visual noise, inconsistent with flat design | `bg-organelle border-b border-white/[0.06]` |
| `text-green-500`, `text-blue-500`, `text-gray-400` | Mixed icon colors create inconsistent visual language | `text-enzyme` (primary), `text-ghost` (secondary), `text-nucleus` (text) |
| `text-white/40`, `text-white/60` | Low contrast fails WCAG AA | `text-protein` (72%), `text-ghost` (38%) |
| `p-4`, `m-6`, `gap-2` | Arbitrary spacing creates inconsistent layout | `p-[tissue]`, `m-[organ]`, `gap-[cell]` |
| No dedicated interrupt button | Users can't easily interrupt voice responses | Google Assistant-style tap-to-interrupt button |

---

## 2. Specification Drafts

### 2.1 Draft: visual-hierarchy Spec

**Purpose**: Define the visual hierarchy system that ensures clear information architecture with consistent sizing, spacing, and contrast ratios.

**Scope**:
- **In Scope**:
  - Text hierarchy (heading levels, body, secondary, tertiary)
  - Spacing hierarchy (margins, padding, gaps)
  - Color hierarchy (backgrounds, borders, text)
  - Size hierarchy (widget sizes, touch targets)
  - Z-index hierarchy (layering)
- **Out of Scope**:
  - Widget implementations (handled by C008)
  - Motion animations (handled by C008 motion presets)
  - Layout system (anchors, mobile stack)

**Locked from LLD** (agentx_organic_ui_design_system.md:18-210):

```typescript
// Text Hierarchy (from tokens.font)
{
  size: {
    xs: '11px',      // Micro labels
    sm: '13px',      // Small text
    base: '15px',    // Body text (Raycast standard)
    md: '17px',      // Medium emphasis
    lg: '20px',      // Large emphasis
    xl: '24px',      // Section headings
    xxl: '32px',     // Page headings
    voice: '48px',   // Voice transcript (large, clear)
  },
  weight: {
    normal: 400,     // Body text
    medium: 500,     // Medium emphasis
    semibold: 600,   // Strong emphasis
    bold: 700,       // Headings
  },
}

// Color Hierarchy (from tokens.color)
{
  void: '#0A0A0A',           // Deepest background
  membrane: '#141414',        // Primary surface
  cytoplasm: '#1C1C1C',       // Secondary surface
  organelle: '#252525',       // Tertiary surface (cards, headers)
  nucleus: 'rgba(255,255,255,0.96)',   // Primary text
  protein: 'rgba(255,255,255,0.72)',   // Secondary text
  ghost: 'rgba(255,255,255,0.38)',     // Tertiary text
  enzyme: '#00D9FF',         // Primary action (single accent)
}

// Spacing Hierarchy (from tokens.space)
{
  nucleus: 4,     // Tight genetic spacing
  cell: 8,        // Base cell
  tissue: 16,     // Tissue cluster (standard padding)
  organ: 24,      // Organ system (large padding)
  organism: 32,   // Full organism
  colony: 48,     // Multi-organism
  ecosystem: 64,  // Layout regions
}

// Size Hierarchy (from tokens.widget, radius)
{
  widget: {
    micro: { w: 180, h: 120 },
    small: { w: 280, h: 200 },
    medium: { w: 380, h: 280 },
    large: { w: 520, h: 380 },
    hero: { w: 720, h: 480 },
  },
  radius: {
    lg: '32px',      // Large organic
    md: '24px',      // Medium organic (standard radius)
    sm: '16px',      // Small organic
    xs: '12px',      // Micro organic
  },
}

// Z-Index Hierarchy (from tokens.layer)
{
  bg: 0,
  metaball: 1,
  surface: 10,
  widget: 20,
  float: 30,
  voice: 40,
  modal: 50,
  toast: 60,
}
```

**Requirements**:
1. FR-VH-001: All text MUST use token-based sizes (no arbitrary font-size)
2. FR-VH-002: All colors MUST use token-based colors (no arbitrary hex codes)
3. FR-VH-003: All spacing MUST use token-based spacing (no arbitrary padding/margin)
4. FR-VH-004: Text contrast MUST meet WCAG AA (4.5:1 for normal text, 3:1 for large text)
5. FR-VH-005: Visual hierarchy MUST be consistent across all components

**Acceptance Criteria**:
- [ ] All text uses token-based sizes (xs → voice)
- [ ] All colors use token-based colors (void → toast)
- [ ] All spacing uses token-based spacing (nucleus → ecosystem)
- [ ] WCAG AA compliance verified (Axe DevTools audit)
- [ ] Visual hierarchy tested on real devices (desktop, tablet, mobile)

---

### 2.2 Draft: flat-design Spec

**Purpose**: Define the flat design system that removes gradients, uses subtle borders, and creates consistent visual surfaces.

**Scope**:
- **In Scope**:
  - Flat header pattern (remove gradients)
  - Subtle border system (1px, low opacity)
  - Surface layering (void → membrane → cytoplasm → organelle)
  - Flat widget backgrounds (no gradients)
- **Out of Scope**:
  - Shadow system (already defined in C008 tokens.shadow)
  - Motion animations (handled by C008 motion presets)

**Locked from LLD** (agentx_organic_ui_design_system.md:24-48, 72-78):

```typescript
// Color Hierarchy (for flat surfaces)
{
  void: '#0A0A0A',           // Deepest background
  membrane: '#141414',        // Primary surface
  cytoplasm: '#1C1C1C',       // Secondary surface
  organelle: '#252525',       // Tertiary surface (cards, headers)
  glassWeak: 'rgba(255,255,255,0.03)',   // Weak glass overlay
  glassMid: 'rgba(255,255,255,0.06)',     // Medium glass overlay
  glassStrong: 'rgba(255,255,255,0.09)',  // Strong glass overlay
}

// Shadow Hierarchy (for depth, not gradients)
{
  cell: '0 2px 8px rgba(0,0,0,0.3)',      // Subtle depth
  float: '0 8px 32px rgba(0,0,0,0.4)',    // Floating element
  deep: '0 16px 64px rgba(0,0,0,0.5)',    // Modal depth
  glow: '0 0 24px rgba(0,217,255,0.3)',   // Enzyme glow
  pulse: '0 0 48px rgba(0,217,255,0.5)',  // Enzyme pulse
}
```

**Requirements**:
1. FR-FD-001: Headers MUST use flat backgrounds (`bg-organelle`)
2. FR-FD-002: Headers MUST use subtle borders (`border-b border-white/[0.06]`)
3. FR-FD-003: No gradients allowed (`bg-gradient-to-*` prohibited)
4. FR-FD-004: Surface layering MUST follow void → membrane → cytoplasm → organelle
5. FR-FD-005: Depth created via shadows, not gradients

**Acceptance Criteria**:
- [ ] All headers use flat backgrounds
- [ ] All headers use subtle borders
- [ ] No gradients found in codebase (grep check)
- [ ] Surface layering consistent
- [ ] Depth created via shadows (token-based)

---

### 2.3 Draft: single-accent Spec

**Purpose**: Define the single accent color system that standardizes all interactive elements to use one consistent accent color (enzyme/cyan).

**Scope**:
- **In Scope**:
  - Primary actions (buttons, links, interactive elements)
  - Icon colors (success, info, warning → all use enzyme)
  - Focus indicators (ring, outline)
  - Active states (selected, pressed)
  - Emphasis (highlight, callout)
- **Out of Scope**:
  - Semantic colors (mitosis green, apoptosis red) - already defined in C008
  - Text hierarchy (nucleus, protein, ghost) - already defined in C008

**Locked from LLD** (agentx_organic_ui_design_system.md:35-42):

```typescript
// Single Accent (cyan life)
{
  enzyme: '#00D9FF',              // Primary action
  enzymeSoft: 'rgba(0,217,255,0.12)',   // Soft background
  enzymeGlow: 'rgba(0,217,255,0.24)',   // Glow effect
}

// Semantic Colors (for special cases only)
{
  mitosis: '#00FF88',        // Success/growth (green)
  apoptosis: '#FF4444',      // Error/death (red)
}
```

**Requirements**:
1. FR-SA-001: All interactive elements MUST use `text-enzyme` or `bg-enzyme`
2. FR-SA-002: Secondary elements MUST use `text-ghost` (not green/gray/blue)
3. FR-SA-003: Focus indicators MUST use `ring-enzyme`
4. FR-SA-004: Active states MUST use enzyme variant (enzymeSoft, enzymeGlow)
5. FR-SA-005: No mixed icon colors (all icons use enzyme or ghost)

**Acceptance Criteria**:
- [ ] All interactive elements use enzyme color
- [ ] All secondary elements use ghost color
- [ ] No mixed icon colors (grep check for green-*, blue-*, gray-*)
- [ ] Focus indicators use enzyme ring
- [ ] Active states use enzyme variants

---

### 2.4 Draft: voice-interrupt Spec

**Purpose**: Define the voice interrupt mechanism that provides a clear, obvious way for users to interrupt voice responses, following Google Assistant patterns.

**Scope**:
- **In Scope**:
  - Interrupt button (desktop: Space, mobile: tap button)
  - Visual feedback (interrupt animation)
  - Touch target compliance (44px minimum)
  - ARIA labels ("Tap to interrupt")
- **Out of Scope**:
  - WebSocket connection (C004)
  - Audio playback (C004)
  - Voice nucleus component (C008)

**Locked from LLD** (agentx_organic_ui_design_system.md:324-334, 782-786):

```typescript
// Interrupt Animation (from motion.interrupt)
{
  initial: { scale: 0.8, opacity: 0 },
  animate: { scale: [0.8, 1.1, 1], opacity: 1 },
  transition: { duration: 0.4, ease: tokens.easing.elastic },
}

// Interrupt Handling (from Voice-Specific UX Rules)
// Desktop: Spacebar or click nucleus during playback
// Mobile: "Tap to interrupt" pill (spawns with interrupt animation)
// On interrupt: fade out current audio, clear queue, reset voice state
```

**Requirements**:
1. FR-VI-001: Interrupt button MUST spawn during audio playback
2. FR-VI-002: Interrupt button MUST use interrupt animation (scale 0.8 → 1.1 → 1)
3. FR-VI-003: Desktop: Space key MUST interrupt voice playback
4. FR-VI-004: Mobile: Tap button MUST interrupt voice playback
5. FR-VI-005: Touch target MUST be ≥44px (44px minimum)
6. FR-VI-006: ARIA label MUST be "Tap to interrupt" or "Press Space to interrupt"

**Acceptance Criteria**:
- [ ] Interrupt button spawns during audio playback
- [ ] Interrupt animation plays (scale 0.8 → 1.1 → 1)
- [ ] Space key interrupts on desktop
- [ ] Tap button interrupts on mobile
- [ ] Touch target ≥44px
- [ ] ARIA label accurate
- [ ] Audio fades out on interrupt
- [ ] Queue cleared on interrupt

---

### 2.5 Draft: spacing-tokens Spec

**Purpose**: Ensure all spacing uses token-based values instead of arbitrary numbers for consistent layout.

**Scope**:
- **In Scope**:
  - Padding (p-* classes)
  - Margin (m-* classes)
  - Gap (gap-* classes for flex/grid)
  - Space (width/height for spacers)
- **Out of Scope**:
  - Component-specific spacing (handled by component props)
  - Responsive spacing (handled by Tailwind responsive variants)

**Locked from LLD** (agentx_organic_ui_design_system.md:60-69):

```typescript
// Spacing Tokens (8px grid + golden ratio variants)
{
  nucleus: 4,     // Tight genetic spacing
  cell: 8,        // Base cell
  tissue: 16,     // Tissue cluster (standard padding)
  organ: 24,      // Organ system (large padding)
  organism: 32,   // Full organism
  colony: 48,     // Multi-organism
  ecosystem: 64,  // Layout regions
}
```

**Requirements**:
1. FR-ST-001: All padding MUST use spacing tokens (p-[nucleus] through p-[ecosystem])
2. FR-ST-002: All margin MUST use spacing tokens (m-[nucleus] through m-[ecosystem])
3. FR-ST-003: All gap MUST use spacing tokens (gap-[nucleus] through gap-[ecosystem])
4. FR-ST-004: No arbitrary spacing values (p-4, m-6, gap-2 prohibited)

**Acceptance Criteria**:
- [ ] All padding uses spacing tokens
- [ ] All margin uses spacing tokens
- [ ] All gap uses spacing tokens
- [ ] No arbitrary spacing found (grep check for p-*, m-*, gap-* where * is number)

---

## 3. API Contracts

### 3.1 REST Endpoints

**Note**: C009 is a UI polish change with no new REST endpoints.

### 3.2 WebSocket Channels

**Note**: C009 uses existing voice WebSocket from C004.

### 3.3 Port Assignments

**Note**: C009 uses existing frontend port 3000 from C007.

---

## 4. Data Model Mappings

### 4.1 Pydantic → Zod Mappings

**Note**: C009 is frontend-only with no backend DTOs.

### 4.2 Shared Types

**Note**: C009 uses existing widget protocol from C007.

---

## 5. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| **C008-organic-ui** | Prerequisite | Provides design tokens (color, space, font, radius, shadow, layer) |
| **C007-frontend-architecture** | Prerequisite | Provides LangGraph server-driven UI pattern |
| **C003-agent-pipeline** | Prerequisite | Provides LangGraph state management |
| **C004-voice-streaming** | Consumer | Voice interrupt consumes audio playback state |

---

**Next Artifact**: validate.md
