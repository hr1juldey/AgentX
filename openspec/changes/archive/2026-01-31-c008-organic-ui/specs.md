# Specs Artifact: c008-organic-ui

**Generated**: 2026-01-29
**Change**: c008-organic-ui
**Schema**: spec-factory v1.0.0

---

## 1. Spec: design-tokens

**File**: `specs/design-tokens/spec.md`

**Purpose**: Define the single source of truth design token system that powers the entire Organic UI, providing frozen constants for colors, spacing, typography, shadows, blur, timing, easing, metaball physics, and platform-aware configurations.

**Key Requirements**:
- Single TypeScript file (`design/tokens.ts`) with all token definitions
- CSS variables auto-generated from tokens
- Tailwind config extends tokens (no duplication)
- Capability detection (isMobile, prefersReducedMotion, getMetaballConfig)
- Platform-aware configurations (mobile vs desktop)

**Token Categories** (11 total):
- color (16 values: void, membrane, cytoplasm, organelle, nucleus, protein, ghost, enzyme, enzymeSoft, enzymeGlow, mitosis, apoptosis, glassWeak, glassMid, glassStrong)
- radius (6 values: cell, bubble, lg, md, sm, xs)
- space (7 values: nucleus, cell, tissue, organ, organism, colony, ecosystem)
- shadow (5 values: cell, float, deep, glow, pulse)
- blur (3 values: light, medium, heavy)
- font (family, size, weight, leading)
- timing (6 values: instant, quick, normal, spawn, morph, drift)
- easing (4 curves: cell, elastic, anticipate, exit)
- metaball (physics, mobile options, radii)
- widget (5 sizes: micro, small, medium, large, hero)
- layer (8 z-index levels: bg, metaball, surface, widget, float, voice, modal, toast)

**Acceptance Criteria**:
- [ ] All token categories defined
- [ ] CSS variables generated in globals.css
- [ ] Tailwind config extends tokens
- [ ] Token values match LLD exactly

---

## 2. Spec: metaball-system

**File**: `specs/metaball-system/spec.md`

**Purpose**: Define the universal metaball system that provides organic fluid merging effects on all platforms with intelligent performance optimization.

**Key Requirements**:
- SVG goo filter implementation
- Platform-aware blur (16px desktop, 12px mobile)
- Blob limits (12 desktop, 6 mobile)
- Simplified physics on mobile (attraction only)
- Auto-disable when FPS <20
- Graceful degradation to clean circles

**Performance Targets**:
- Desktop: ≥60fps with 12 blobs
- Mobile: ≥30fps with 6 blobs
- Auto-disable: FPS <20 for 3 consecutive seconds

**Acceptance Criteria**:
- [ ] SVG goo filter renders metaball merging
- [ ] Platform-aware blur applied
- [ ] Blob limits enforced
- [ ] Physics simplified on mobile
- [ ] Auto-disable triggers when FPS <20
- [ ] Graceful degradation to circles

---

## 3. Spec: voice-nucleus

**File**: `specs/voice-nucleus/spec.md`

**Purpose**: Define the central voice interface component that serves as the visual and interaction hub for all voice operations.

**Key Requirements**:
- Platform-aware sizing (160px desktop, 72px mobile)
- Platform-aware positioning (center desktop, bottom-center mobile)
- Pulse animation when active
- Drift animation when idle
- Full accessibility support

**Accessibility**:
- Touch target ≥44px (72px satisfies)
- Keyboard accessible (Space key toggle)
- Screen reader labels ("Start speaking" / "Stop speaking")
- Reduced motion support

**Acceptance Criteria**:
- [ ] Nucleus size platform-aware
- [ ] Position platform-aware
- [ ] Pulse animation when active
- [ ] Drift animation when idle
- [ ] Keyboard and screen reader accessible

---

## 4. Spec: motion-presets

**File**: `specs/motion-presets/spec.md`

**Purpose**: Define reusable motion presets that provide consistent animation behavior across all UI components, following biological metaphors.

**Key Requirements**:
- 9 motion presets (mitosis, pulse, drift, lift, compress, drag, morph, stream, interrupt)
- Stagger presets (container, item)
- All values reference tokens (no hardcoded values)
- Reduced motion support

**Motion Presets**:
- **mitosis**: Widget spawning (380ms, elastic easing)
- **pulse**: Voice active state (1.4s, infinite repeat)
- **drift**: Idle floating (2.4s, infinite repeat)
- **lift**: Hover effect (150ms)
- **compress**: Tap effect (80ms)
- **drag**: Dragging state
- **morph**: Shape transformation (520ms)
- **stream**: Text streaming (150ms)
- **interrupt**: Attention grab (400ms)

**Acceptance Criteria**:
- [ ] All 9 presets defined
- [ ] Stagger presets defined
- [ ] All values reference tokens
- [ ] Reduced motion respected

---

## 5. Cross-Domain Contracts

### 5.1 Shared Types

```typescript
// Widget Protocol (from C007)
type WidgetType =
  | 'markdown'
  | 'card'
  | 'form'
  | 'progress'
  | 'action'
  | 'confirmation'
  | 'image'
  | 'gallery'
  | 'chart'
  | 'searchResult'
  | 'hopProgress'
  | 'citationCard'

// Capability Detection
interface MetaballConfig {
  enabled: boolean
  blur: number  // 16 (desktop) or 12 (mobile)
  maxBlobs: number  // 12 (desktop) or 6 (mobile)
  simplifyPhysics: boolean  // true on mobile
}
```

### 5.2 Integration Points

| Domain A | Domain B | Interface |
|----------|----------|-----------|
| **design-tokens** | **metaball-system** | `capability.getMetaballConfig()` returns platform-aware config |
| **design-tokens** | **voice-nucleus** | `capability.isMobile()` determines size/position |
| **design-tokens** | **motion-presets** | All motion presets reference `tokens.timing`, `tokens.easing` |
| **metaball-system** | **voice-nucleus** | Voice nucleus provides position/radius for metaball blob |
| **C007-frontend-architecture** | **All C008 specs** | LangGraph server-driven UI (`push_ui_message()`, `LoadExternalComponent`) |
| **C003-agent-pipeline** | **All C008 specs** | LangGraph state management with `ui_message_reducer` |
| **C004-voice-streaming** | **voice-nucleus** | Voice WebSocket for audio streaming |

### 5.3 Component Registration (from C007)

```typescript
// src/agent/ui.tsx (colocated with graph.py)
export default {
  markdown: MarkdownComponent,
  card: CardComponent,
  form: FormComponent,
  progress: ProgressComponent,
  action: ActionComponent,
  confirmation: ConfirmationComponent,
  image: ImageComponent,
  gallery: GalleryComponent,
  chart: ChartComponent,
  searchResult: SearchResultComponent,
  hopProgress: HopProgressComponent,
  citationCard: CitationCardComponent,
};
```

---

**Next Artifact**: design.md
