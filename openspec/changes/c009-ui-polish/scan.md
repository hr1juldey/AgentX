# Scan Artifact: c009-ui-polish

**Generated**: 2026-01-29
**Change**: c009-ui-polish
**Schema**: spec-factory v1.0.0

---

## 1. LLD Synthesis

### 1.1 Relevant LLD Documents

| Document | Path | Relevance |
|----------|------|-----------|
| Incremental Release Plan | `/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/incremental_release_plan.md` | Phase 9 definition: UI Polish |
| C008 Organic UI Design System | `/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/agentx_organic_ui_design_system.md` | Design tokens, motion presets |
| C006 Release Plan Specs | `/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c006-release-plan/specs.md` | Phase 9: UI Polish (Raycast minimalism, GA clarity) |
| Plan File (Session Summary) | `/home/riju279/.claude/plans/golden-skipping-hedgehog.md` | R014 aesthetic issues → fixes |
| R014 UI Showcase | `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/` | Reference implementation (aesthetic issues identified) |

### 1.2 Locked Definitions from LLD

#### Phase 9 Definition (Locked from incremental_release_plan.md and c006-release-plan/specs.md:85)

```markdown
Phase 9: UI Polish
- Duration: 2-3 hours
- Focus: Raycast minimalism, Google Assistant voice clarity, aesthetic fixes
- Deliverables: Refined UI with professional polish
- APIs Frozen: Aesthetics
```

#### R014 Aesthetic Issues (Locked from plan exploration)

```markdown
Aesthetic Issues Identified in R014:
1. Gradient headers (chart) → Remove, use flat like markdown
2. Icon colors (green/gray/blue mix) → Standardize to single accent color
3. Dev console (poor contrast) → Improve contrast ratios
4. Inconsistent spacing → Add spacing tokens

Fixes Required:
1. ❌ Remove gradient headers (use flat like markdown)
2. ❌ Standardize icon colors (single accent, not green/gray/blue)
3. ❌ Improve dev console contrast
4. ✅ Add consistent spacing tokens (from C008)
5. ✅ Reference Raycast #1a1a1a dark theme
6. ✅ Reference Google Assistant voice interrupt button
```

#### Design Token Refinements (from C008)

```typescript
// Raycast-inspired dark theme (already in C008 tokens)
void: '#0A0A0A'      // Deep space (close to Raycast #1a1a1a)
membrane: '#141414'   // Primary surface
cytoplasm: '#1C1C1C'  // Secondary surface
organelle: '#252525'  // Tertiary surface

// Single accent (cyan life)
enzyme: '#00D9FF'     // Primary action

// Spacing tokens (already in C008)
nucleus: 4
cell: 8
tissue: 16
organ: 24
organism: 32
colony: 48
ecosystem: 64
```

---

## 2. Codebase Exploration (opsx:explore)

### 2.1 Exploration Topics

```
1. R014 aesthetic issues (gradient headers, icon colors, dev console contrast)
2. Raycast minimalism patterns (flat design, consistent spacing, single accent)
3. Google Assistant voice clarity (interrupt button, visual hierarchy)
4. C008 design token integration (using existing tokens for consistency)
5. Layout refinements (widget spacing, padding, margins)
```

### 2.2 File Inventory

#### Backend Files
| File | Lines | Purpose |
|------|-------|---------|
| N/A | N/A | C009 is frontend-only, no backend changes |

#### Frontend Files (References)
| File | Lines | Purpose |
|------|-------|---------|
| `docs/engineering/agentx_organic_ui_design_system.md` | 1116 | Design tokens, motion presets (C008 reference) |
| `prototypes/R014_ui_showcase/frontend/components/ui/` | 229+ | Reference: Aesthetic issues to fix |
| `openspec/changes/c008-organic-ui/design/tokens.ts` | ~180 | Single source of truth for tokens |
| `openspec/changes/c008-organic-ui/design/motion.ts` | ~150 | Motion presets (may need refinements) |

---

## 3. Patterns Discovered

### 3.1 Architectural Patterns

**1. Raycast Minimalism**
- Flat design (no gradients, no shadows except for depth)
- Consistent spacing (4px grid system)
- Single accent color (cyan for AgentX)
- Monochrome base with one accent
- Subtle borders (1px, low opacity)
- High contrast text (96% white on dark backgrounds)

**2. Google Assistant Voice Clarity**
- Clear visual hierarchy (voice button is largest element)
- Obvious interrupt mechanism (dedicated button or tap gesture)
- Minimal chrome (focus on content, not UI)
- Generous touch targets (44px minimum)
- Clear feedback (pulse animation when active)

**3. C008 Token Integration**
- All aesthetic refinements use existing tokens from C008
- No new tokens needed (C008 already comprehensive)
- Consistent spacing using space.tissue (16px), space.organ (24px)
- Consistent colors using void, membrane, organelle, nucleus, enzyme

### 3.2 Code Patterns

**1. Flat Header Pattern** (vs R014 gradient)
```typescript
// Wrong (R014 gradient):
<div className="bg-gradient-to-r from-void to-membrane" />

// Right (flat, like markdown):
<div className="bg-organelle border-b border-white/[0.06]" />
```

**2. Single Accent Icon Pattern** (vs R014 mixed colors)
```typescript
// Wrong (R014 mixed colors):
<Icon className="text-green-500" />
<Icon className="text-gray-400" />
<Icon className="text-blue-500" />

// Right (single accent):
<Icon className="text-enzyme" />           // Primary action
<Icon className="text-ghost" />            // Secondary
<Icon className="text-nucleus" />          // Primary text
```

**3. Spacing Token Pattern** (consistent spacing)
```typescript
// Use spacing tokens instead of arbitrary values
className="p-4"           // ❌ Arbitrary (16px)
className="p-[tissue]"    // ✅ Token-based
className="gap-6"         // ❌ Arbitrary (24px)
className="gap-[organ]"   // ✅ Token-based
```

**4. High Contrast Text Pattern**
```typescript
// Wrong (low contrast):
<p className="text-white/60">Secondary text</p>

// Right (high contrast, from tokens):
<p className="text-protein">Secondary text</p>  // 72% white
<p className="text-ghost">Tertiary text</p>    // 38% white
```

### 3.3 Anti-Patterns to Avoid

**1. Don't Use Gradients**
- ❌ Old approach: `bg-gradient-to-r from-void to-membrane`
- ✅ New approach: `bg-organelle border-b border-white/[0.06]`

**2. Don't Mix Icon Colors**
- ❌ Old approach: Green (success), gray (disabled), blue (info)
- ✅ New approach: Enzyme (primary), ghost (secondary), nucleus (text)

**3. Don't Use Arbitrary Spacing**
- ❌ Old approach: `p-4`, `m-6`, `gap-2`
- ✅ New approach: `p-[tissue]`, `m-[organ]`, `gap-[cell]`

**4. Don't Ignore Contrast Ratios**
- ❌ Old approach: `text-white/40` (fails WCAG AA)
- ✅ New approach: `text-protein` (72% white, passes WCAG AA)

---

## 4. Reference Analysis

### 4.1 Mimicus Patterns (Copy Concepts, Not Names)

| Concept | Mimicus Pattern | Intended Use |
|---------|-----------------|--------------|
| Clean Architecture | core/, domain/, application/, infrastructure/, presentation/ | Not applicable for UI polish |
| Repository | ABC base class + implementations | Not applicable for UI polish |
| Entity | @dataclass with business methods | Not applicable for UI polish |
| Use Case | Single-purpose classes with execute() | Not applicable for UI polish |

**Note**: C009 is a frontend UI polish change with no backend patterns.

### 4.2 R014 Reference (Concepts Only)

| Concept | R014 Approach | Improved Approach |
|---------|---------------|-------------------|
| **Gradient Headers** | `bg-gradient-to-r from-void to-membrane` | Remove, use flat `bg-organelle border-b` |
| **Icon Colors** | Green (success), gray (disabled), blue (info) | Single accent: enzyme (primary), ghost (secondary), nucleus (text) |
| **Dev Console Contrast** | Low contrast text (fails WCAG) | High contrast: nucleus (96%), protein (72%), ghost (38%) |
| **Spacing** | Arbitrary values (p-4, m-6, gap-2) | Token-based: p-[tissue], m-[organ], gap-[cell] |
| **Dark Theme** | Custom dark colors | Raycast-inspired: void #0A0A0A (close to #1a1a1a) |
| **Voice Interrupt** | No dedicated interrupt button | Google Assistant-style: clear tap-to-interrupt button with interrupt animation |

**R014 Problems Fixed**:
- R014 had gradient headers (visual noise)
- R014 had mixed icon colors (inconsistent visual language)
- R014 had poor dev console contrast (accessibility issue)
- R014 had arbitrary spacing (inconsistent layout)

**C009 Improvements**:
- Flat headers (Raycast minimalism)
- Single accent color (consistent visual language)
- High contrast text (WCAG AA compliance)
- Token-based spacing (consistent layout)
- Voice interrupt button (Google Assistant clarity)

---

## 5. Key Files for This Change

```
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/agentx_organic_ui_design_system.md
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c008-organic-ui/design/tokens.ts
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c008-organic-ui/design/motion.ts
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/frontend/components/ui/
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c006-release-plan/specs.md
```

---

**Next Artifact**: extract.md
