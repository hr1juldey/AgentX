# Spec: motion-presets

**File**: `specs/motion-presets/spec.md`

## 1.1 Purpose

Define reusable motion presets that provide consistent animation behavior across all UI components, following biological metaphors (mitosis, pulse, drift) and referencing the single source of truth design token system.

## 1.2 Scope

**In Scope**:
- 9 motion presets: mitosis, pulse, drift, lift, compress, drag, morph, stream, interrupt
- Stagger presets: container, item
- Integration with Framer Motion
- Reference to design tokens (no hardcoded values)
- Reduced motion support

**Out of Scope**:
- Physics simulation (metaball-system spec)
- Component implementations (voice-nucleus spec)
- Layout animations (widget spawning, anchor positioning)
- Framer Motion library installation

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-MP-001 | All presets MUST reference tokens (no hardcoded values) | Must |
| FR-MP-002 | Timing MUST follow biological metaphors (spawn 380ms, pulse 1.4s, drift 2.4s) | Must |
| FR-MP-003 | Easing MUST use organic curves (elastic, cell, anticipate) | Must |
| FR-MP-004 | Stagger MUST support configurable delays (staggerChildren, delayChildren) | Must |
| FR-MP-005 | Stream preset MUST handle token chunking (200ms windows) | Must |
| FR-MP-006 | All presets MUST respect `prefers-reduced-motion` | Must |
| FR-MP-007 | Presets MUST be compatible with Framer Motion | Must |
| FR-MP-008 | File MUST be under 200 lines | Should |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-MP-001 | Preset objects MUST be frozen (no runtime modifications) | Should |
| NFR-MP-002 | TypeScript types MUST be exported for each preset | Should |

## 1.4 Data Model

**Locked from LLD** (agentx_organic_ui_design_system.md:214-349):

```typescript
// design/motion.ts
import { tokens } from './tokens'

export const motion = {
  // Cell division - widget spawning
  mitosis: {
    initial: { scale: 0, opacity: 0, filter: 'blur(12px)' },
    animate: { scale: 1, opacity: 1, filter: 'blur(0px)' },
    exit: { scale: 0.8, opacity: 0, filter: 'blur(8px)' },
    transition: {
      duration: tokens.timing.spawn / 1000,  // 0.38s
      ease: tokens.easing.elastic,  // [0.68, -0.55, 0.265, 1.55]
    },
  },

  // Nucleus pulse - voice active state
  pulse: {
    animate: {
      scale: [1, 1.08, 1],
      boxShadow: [tokens.shadow.glow, tokens.shadow.pulse, tokens.shadow.glow],
    },
    transition: {
      duration: 1.4,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },

  // Idle floating - breathing motion
  drift: {
    animate: { y: [0, -8, 0], x: [0, 4, 0] },
    transition: {
      duration: tokens.timing.drift / 1000,  // 2.4s
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },

  // Hover - subtle lift
  lift: {
    whileHover: {
      scale: 1.02,
      y: -2,
      boxShadow: tokens.shadow.float,
    },
    transition: {
      duration: tokens.timing.quick / 1000,  // 0.15s
    },
  },

  // Press - quick compression
  compress: {
    whileTap: { scale: 0.96 },
    transition: {
      duration: tokens.timing.instant / 1000,  // 0.08s
    },
  },

  // Drag - emphasized state
  drag: {
    whileDrag: {
      scale: 1.05,
      boxShadow: tokens.shadow.deep,
      cursor: 'grabbing',
      zIndex: tokens.layer.float + 10,  // 40
    },
  },

  // Morph - shape transformation
  morph: {
    transition: {
      duration: tokens.timing.morph / 1000,  // 0.52s
      ease: tokens.easing.cell,  // [0.25, 0.1, 0.25, 1]
    },
  },

  // Text streaming - progressive reveal
  stream: {
    initial: { opacity: 0, x: -8 },
    animate: { opacity: 1, x: 0 },
    transition: {
      duration: tokens.timing.quick / 1000,  // 0.15s
      ease: tokens.easing.anticipate,  // [0.22, 1, 0.36, 1]
    },
  },

  // Interrupt signal - attention grab
  interrupt: {
    initial: { scale: 0.8, opacity: 0 },
    animate: { scale: [0.8, 1.1, 1], opacity: 1 },
    transition: {
      duration: 0.4,
      ease: tokens.easing.elastic,  // [0.68, -0.55, 0.265, 1.55]
    },
  },
}

// Stagger children animations
export const stagger = {
  container: {
    animate: {
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.1,
      },
    },
  },
  item: motion.stream,
}
```

## 1.5 API Contract

**Note**: This spec has no API contracts (frontend-only).

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-MP-001 | All timing values MUST reference `tokens.timing` | Code review / Linter |
| BR-MP-002 | All easing values MUST reference `tokens.easing` or standard names | Code review / Linter |
| BR-MP-003 | All shadow values MUST reference `tokens.shadow` | Code review / Linter |
| BR-MP-004 | Presets MUST NOT be modified at runtime | TypeScript `as const` |
| BR-MP-005 | Reduced motion MUST be respected (components check `capability.prefersReducedMotion()`) | Runtime check |

## 1.7 Acceptance Criteria

- [ ] All 9 presets defined (mitosis, pulse, drift, lift, compress, drag, morph, stream, interrupt)
- [ ] Stagger presets defined (container, item)
- [ ] All timing values reference `tokens.timing`
- [ ] All easing values reference `tokens.easing` or standard names
- [ ] All shadow values reference `tokens.shadow`
- [ ] All z-index values reference `tokens.layer`
- [ ] File created at `design/motion.ts`
- [ ] File under 200 lines
- [ ] TypeScript types exported for each preset
- [ ] Presets integrate with Framer Motion
- [ ] Reduced motion respected (components check before using)
- [ ] Mitosis timing: 380ms
- [ ] Pulse duration: 1.4s
- [ ] Drift duration: 2.4s
- [ ] Stream timing: 150ms
- [ ] Interrupt duration: 0.4s
- [ ] Stagger delays: 0.08s (staggerChildren), 0.1s (delayChildren)
