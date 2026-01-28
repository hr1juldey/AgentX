# Spec: visual-hierarchy

**File**: `specs/visual-hierarchy/spec.md`

## 1.1 Purpose

Define the visual hierarchy system that ensures clear information architecture with consistent sizing, spacing, and contrast ratios.

## 1.2 Scope

**In Scope**:
- Text hierarchy (heading levels, body, secondary, tertiary)
- Spacing hierarchy (margins, padding, gaps)
- Color hierarchy (backgrounds, borders, text)
- Size hierarchy (widget sizes, touch targets)
- Z-index hierarchy (layering)

**Out of Scope**:
- Widget implementations (handled by C008)
- Motion animations (handled by C008 motion presets)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VH-001 | All text MUST use token-based sizes (no arbitrary font-size) | Must |
| FR-VH-002 | All colors MUST use token-based colors (no arbitrary hex codes) | Must |
| FR-VH-003 | All spacing MUST use token-based spacing (no arbitrary padding/margin) | Must |
| FR-VH-004 | Text contrast MUST meet WCAG AA (4.5:1 for normal text, 3:1 for large text) | Must |
| FR-VH-005 | Visual hierarchy MUST be consistent across all components | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-VH-001 | Token usage MUST be verifiable via grep | Should |
| NFR-VH-002 | WCAG AA compliance MUST be verifiable via Axe DevTools | Should |

## 1.4 Data Model

**Locked from C008** (agentx_organic_ui_design_system.md:88-115):

```typescript
// Text Hierarchy
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
}

// Color Hierarchy
{
  void: '#0A0A0A',           // Deepest background
  membrane: '#141414',        // Primary surface
  cytoplasm: '#1C1C1C',       // Secondary surface
  organelle: '#252525',       // Tertiary surface
  nucleus: 'rgba(255,255,255,0.96)',   // Primary text
  protein: 'rgba(255,255,255,0.72)',   // Secondary text
  ghost: 'rgba(255,255,255,0.38)',     // Tertiary text
  enzyme: '#00D9FF',         // Primary action
}

// Spacing Hierarchy
{
  nucleus: 4,     // Tight genetic spacing
  cell: 8,        // Base cell
  tissue: 16,     // Tissue cluster (standard padding)
  organ: 24,      // Organ system (large padding)
  organism: 32,   // Full organism
  colony: 48,     // Multi-organism
  ecosystem: 64,  // Layout regions
}

// Z-Index Hierarchy
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

## 1.5 Acceptance Criteria

- [ ] All text uses token-based sizes
- [ ] All colors use token-based colors
- [ ] All spacing uses token-based spacing
- [ ] WCAG AA compliance verified (Axe DevTools audit)
- [ ] Visual hierarchy tested on real devices
