# Proposal: Physics-Based Cell Division Voice Component

## Why

Inspired by the Kotlin ExpandableFAB pattern from sinasamaki/metaBalls—where satellites orbit a central nucleus and expand outward on click—we want to create an audio-reactive version where **speaking splits cells apart** and **silence merges them back**. This implements the same metaball merging behavior but triggered by continuous audio energy instead of binary click state, housed in a design library to avoid breaking the existing working voice button.

## What Changes

### Core Component
- **Audio-Reactive Cell Division**: 4-12 orbiting cells that push outward based on accumulated audio energy (not instant audio level)
- **Physics Engine**: Energy → velocity → position with spring damping and momentum (not binary `expanded` state)
- **Metaball Merge Behavior**: Low energy (silence) → cells merge with nucleus via blur; high energy (speaking) → cells split and orbit independently
- **Continuous Orbiting**: Cells rotate around nucleus while expanding/contracting (counter-rotation pattern like ProgressLoader)

### Design Library System
- **Main → Library Navigation**: Add header button (top-right) to navigate from main page to design library
- **Library Index Page**: `/library` route showcasing all experimental components as cards/thumbnails
- **Component Isolation Pages**: `/library/[component-name]` routes where each component runs in isolation with:
  - Full viewport demo area
  - Back button to return to library index
  - Component description and controls
  - No external layout dependencies

### Route Structure
```
/                          (main page, existing)
  └─→ [Header: "Design Library" button]
       ↓
/library                   (library index, new)
  ├─→ Physics Cells (card/thumbnail)
  ├─→ [Future components...]
  └─→ [Back to Main]
       ↓
/library/physics-cells     (component demo page, new)
  ├─→ Full viewport demo
  ├─→ Description & controls
  └─→ [← Back to Library]
```

## Capabilities

### New Capabilities
- `physics-based-cell-division`: Audio-triggered orbiting cells with energy accumulation physics, inspired by ExpandableFAB's satellite pattern but with continuous audio input instead of click trigger
- `design-library`: Multi-page design system with library index, isolated component demo pages, and navigation hierarchy (main → library → component → back)

### Modified Capabilities
None - this is a new standalone component in a separate route, not a modification to existing voice button behavior

## Impact

**Affected Code**:
```
frontend/src/
├── app/
│   ├── library/
│   │   ├── page.tsx                    # Library index (new)
│   │   └── physics-cells/
│   │       └── page.tsx                # Component demo page (new)
│   └── layout.tsx                      # Add header navigation (modify)
├── components/
│   ├── physics-cells-voice.tsx         # Main component (new)
│   ├── layout/
│   │   └── library-header.tsx          # Shared header for library pages (new)
│   └── library/
│       ├── component-card.tsx          # Library index card (new)
│       └── demo-container.tsx          # Isolated demo wrapper (new)
└── lib/physics/
    ├── energy-accumulator.ts           # Energy state management (new)
    ├── orbit-physics.ts                # Position/velocity calculator (new)
    └── spring-damping.ts               # Spring physics utilities (new)
```

**Dependencies**:
- None new (uses existing Web Audio API, React hooks, Next.js App Router)

**APIs**:
- No backend changes (frontend-only component)

**Systems**:
- Next.js App Router (new routes: `/library`, `/library/physics-cells`)
- Existing design tokens and color scheme
- Existing metaball filter infrastructure
