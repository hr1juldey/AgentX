# Design: Physics-Based Cell Division Voice Component

## Context

**Current State**: The existing `voice-button-kyutai-direct.tsx` component uses direct audio-level-to-distance mapping with 3-6 orbiting blobs. When audio pushes blobs outward to distance 0.85 with larger radii, they get clipped by the 224px viewBox. The component is production-critical (main voice interface) so experimental visual changes are risky.

**Inspiration**: Kotlin's ExpandableFAB from sinasamaki/metaBalls demonstrates satellite expansion with spring animations and metaball merging. The key pattern is:
- Binary state: `expanded = true | false`
- Spring animation: `animateDpAsState(0.dp → 120.dp)`
- Satellites at cardinal directions (up, left, right, center)
- Metaball blur (`blur=50f`) merges nearby circles

**User's Vision**: Adapt ExpandableFAB's visual behavior to audio input—where **speaking** provides the energy to split cells apart, and **silence** causes them to gravitate back and merge with the central nucleus.

**Constraints**:
- Must not break existing working voice button
- Must use Next.js App Router for routing
- Must reuse existing metaball filter infrastructure
- Must work on mobile (responsive design)
- Must handle microphone permissions gracefully

## Goals / Non-Goals

**Goals:**
1. Create isolated design library at `/library` with component showcase
2. Implement physics-based cell division component with 4-12 orbiting cells
3. Audio energy accumulation (not instant mapping) with momentum
4. Seamless merge/split behavior based on silence vs speech
5. Full viewport demo pages with back-button navigation

**Non-Goals:**
- Replacing the existing `voice-button-kyutai-direct.tsx` component
- Real-time voice chat integration (demo-only visual component)
- Persistent audio context across page navigations
- Backend API changes (frontend-only)

## Decisions

### 1. Physics Engine: Energy Accumulation vs Direct Mapping

**Decision**: Use energy accumulation with spring-damped velocity, not direct `distance = audioLevel * maxDistance` mapping.

**Rationale**:
- Direct mapping feels "jittery" and unnatural (ExpandableFAB uses spring physics for smoothness)
- Energy accumulation provides momentum—cells don't snap instantly on silence
- More organic "cell division" metaphor: energy builds up → cells push outward

**Alternatives Considered**:
| Approach | Pros | Cons | Chosen |
|----------|------|------|--------|
| Direct mapping | Simple, predictable | Jittery, no momentum | ✗ |
| Smoothed average | Less jitter | Still feels mechanical | ✗ |
| Energy accumulation | Natural momentum, smooth | More complex | ✓ |

**Implementation**:
```typescript
// Per-frame physics update
energy += audioLevel * ENERGY_GAIN;      // Accumulate from audio
energy *= ENERGY_DECAY;                  // Decay when silent
targetDistance = base + (energy * MAX);  // Energy → target
velocity = (target - current) * SPRING;  // Spring force
newDistance = current + velocity;        // Apply momentum
```

### 2. Route Structure: Flat vs Nested

**Decision**: Use flat routes `/library/physics-cells` instead of nested `/library/[slug]/[component]`.

**Rationale**:
- Simpler routing (no dynamic slug handling needed)
- Easier to add specific pages later (`/library/physics-cells/docs`)
- Clear URL structure for bookmarking

**Alternatives Considered**:
| Structure | Pros | Cons | Chosen |
|-----------|------|------|--------|
| `/library/[component]` | Dynamic, extensible | Requires slug mapping | ✗ |
| `/library/physics-cells` | Explicit, simple | Manual per-component routes | ✓ |

### 3. Component Isolation: Fresh Mount vs Shared Context

**Decision**: Each component demo page gets a fresh React component mount with its own audio context.

**Rationale**:
- No shared state between demos (cleaner testing)
- Each demo has explicit "Enable Mic" button (permissions handling)
- Simpler mental model—each demo is self-contained

**Trade-off**: Slightly more boilerplate per demo page, but worth it for isolation guarantees.

### 4. Cell Count: Fixed vs Configurable

**Decision**: Make cell count configurable via props with sensible default (8 cells).

**Rationale**:
- User requested "4 to 12 cells" – configurable allows experimentation
- Default of 8 provides good visual density
- Easy to adjust per-demo without code changes

**Implementation**:
```typescript
interface PhysicsCellsProps {
  cellCount?: number;  // Default: 8
  blur?: number;       // Default: 16 (from design tokens)
  nucleusRadius?: number;
}
```

### 5. Metaball Filter: Reuse vs New Implementation

**Decision**: Reuse existing metaball filter infrastructure from `voice-button-kyutai-direct.tsx`.

**Rationale**:
- Filter already tested and working
- Design tokens already define blur values
- Consistent visual language across components

**Filter Structure**:
```svg
<filter id="goo-physics-cells">
  <feGaussianBlur in="SourceGraphic" stdDeviation={blur} result="blur" />
  <feColorMatrix in="blur" mode="matrix"
    values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -7" result="goo" />
</filter>
```

### 6. ViewBox Sizing: Fixed vs Dynamic

**Decision**: Calculate viewBox dynamically based on max cell distance + padding.

**Rationale**:
- Fixed viewBox risks clipping (current bug at 0.85 distance)
- Dynamic viewBox accommodates any cell count/orbit configuration
- Formula: `viewBox = (nucleusRadius * MAX_DISTANCE * 2) + (blur * 4)`

**Calculation**:
```typescript
const maxReach = nucleusRadius * CONFIG.MAX_DISTANCE;  // 160 * 0.75 = 120px
const padding = blur * 3;  // 48px
const viewBoxSize = (maxReach + padding) * 2;  // ~336px
```

## Architecture

### File Structure

```
frontend/src/
├── app/
│   ├── library/
│   │   ├── page.tsx                    # Library index (grid of cards)
│   │   └── physics-cells/
│   │       └── page.tsx                # Component demo (full viewport)
│   └── layout.tsx                      # Root layout (add LibraryHeader)
│
├── components/
│   ├── physics-cells-voice.tsx         # Main reusable component
│   ├── layout/
│   │   └── library-header.tsx          # <Back> <Title> <ThemeToggle>
│   └── library/
│       ├── component-card.tsx          # Clickable card with thumbnail
│       └── demo-container.tsx          # Wrapper: description + demo area
│
├── lib/physics/
│   ├── energy-accumulator.ts           # updateEnergy(audioLevel): energy
│   ├── orbit-physics.ts                # updateCell(cell, energy): cell
│   └── spring-damping.ts               # springDamped(target, current): velocity
│
└── types/
    └── library.ts                      # LibraryComponent, ComponentCategory
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUDIO → PHYSICS → RENDER                            │
└─────────────────────────────────────────────────────────────────────────────┘

Web Audio API
    │
    ├─→ AnalyserNode.getByteFrequencyData()
    │
    ▼
Audio Level (0-1)
    │
    ├─→ energyAccumulator.accumulate(audioLevel)
    │       Returns: energy (0-1)
    │
    ▼
Energy State
    │
    ├─→ orbitPhysics.updateAllCells(cells, energy)
    │       For each cell:
    │       - angle += speed
    │       - targetDistance = base + (energy * MAX)
    │       - velocity = springDamped(target, current)
    │       - distance += velocity
    │       - radius = base * breathingScale * energyScale
    │
    ▼
Updated Cells (array of {angle, distance, radius, ...})
    │
    ├─→ SVG rendering with metaball filter
    │       - If distance < blur/2: cells merge with nucleus
    │       - If distance > blur/2: cells orbit independently
    │
    ▼
Visual Output (silence=merged blob, speech=split satellites)
```

### Physics Constants

```typescript
const CONFIG = {
  // Cell configuration
  cellCount: 8,
  baseDistance: 0.15,        // "Home" position when silent
  mergeThreshold: 0.25,      // Below this: blur merges cells
  splitThreshold: 0.50,      // Above this: cells separate visibly
  maxDistance: 0.75,         // Maximum outward reach

  // Energy accumulation
  energyGainRate: 0.08,      // Audio → energy conversion
  energyDecayRate: 0.96,     // Silence energy loss per frame

  // Spring physics
  springStiffness: 0.15,     // Pull toward target distance
  damping: 0.85,             // Velocity decay (momentum)

  // Orbital mechanics
  nucleusRotationSpeed: 0.0003,  // Slow CCW rotation
  orbitSpeedRange: [0.0003, 0.0007],  // Cell orbital speed range

  // Rendering
  nucleusRadius: 160,        // Desktop (72 mobile)
  cellRadiusRange: [20, 40], // Cell size variation
  blur: 16,                  // Metaball blur radius
};
```

## Risks / Trade-offs

### Risk 1: Performance with 12 Cells + Physics

**Risk**: 12 cells × 60 FPS physics updates may cause frame drops on mobile.

**Mitigation**:
- Default to 8 cells (balanced performance/visuals)
- Use `requestAnimationFrame` for efficient updates
- Profile on low-end devices before release

### Risk 2: Microphone Permissions Rejected

**Risk**: User denies mic permission → demo becomes non-functional.

**Mitigation**:
- Graceful degradation: Show static "Enable Mic" button with explanation
- Fallback to "Demo Mode" with simulated audio levels (sine wave)
- Clear error messaging in UI

### Risk 3: ViewBox Still Clips on Edge Cases

**Risk**: Dynamic viewBox calculation may still clip with extreme configurations.

**Mitigation**:
- Add safety margin (blur * 3 instead of blur * 2)
- Cap maxDistance at 0.75 (not 1.0) to prevent extreme reach
- Document viewBox limitations in component props

### Risk 4: Cross-Browser Metaball Filter Inconsistency

**Risk**: SVG filters may render differently across browsers.

**Mitigation**:
- Test on Chrome, Firefox, Safari (desktop + mobile)
- Consider CSS `backdrop-filter` as fallback for modern browsers
- Document known browser limitations

## Migration Plan

### Phase 1: Library Infrastructure (Foundation)
1. Create `/library` route with header navigation
2. Implement `LibraryHeader` component with back button
3. Add "Design Library" button to main page header
4. Test navigation flow: main → library → main

### Phase 2: Physics Engine
1. Implement `energy-accumulator.ts` (unit tests for energy curves)
2. Implement `spring-damping.ts` (verify spring behavior matches ExpandableFAB)
3. Implement `orbit-physics.ts` (test cell position updates)
4. Integrate all three in `usePhysicsCells` hook

### Phase 3: Component Implementation
1. Create `physics-cells-voice.tsx` (reusable component)
2. Implement `/library/physics-cells/page.tsx` (demo page)
3. Add audio context handling (permissions, start/stop)
4. Test merge/split behavior with real microphone input

### Phase 4: Library Index
1. Create `component-card.tsx` (thumbnail + title + "View Demo" button)
2. Implement `/library/page.tsx` (grid layout with Physics Cells card)
3. Add component metadata (title, description, thumbnail)
4. Test responsive layout (mobile/tablet/desktop)

### Rollback Strategy
- Each phase is independently deployable
- Library routes don't affect main app functionality
- If physics engine causes issues, can revert to simple direct mapping
- Navigation changes are additive (no existing routes modified)

## Open Questions

1. **Thumbnail Generation**: How to create component thumbnails for library index?
   - Option A: Static screenshots in `public/library/thumbnails/`
   - Option B: Generate programmatically with headless browser
   - **Decision**: Start with Option A (simpler), consider B later

2. **Component Metadata Storage**: Where to store library component catalog?
   - Option A: Hardcoded array in `/library/page.tsx`
   - Option B: JSON file at `/lib/components.json`
   - Option C: Database-driven (future-proof for many components)
   - **Decision**: Start with Option A, migrate to B if >5 components

3. **Audio Context Persistence**: Should audio continue when navigating away?
   - Option A: Stop audio on page unmount (current plan)
   - Option B: Keep audio context in global state (more complex)
   - **Decision**: Option A (simpler, aligns with "isolated demos" goal)

4. **Cell Count Control**: Expose as slider or preset buttons?
   - Option A: Slider (4-12 range)
   - Option B: Preset buttons [4] [6] [8] [10] [12]
   - **Decision**: Option B (clearer UX, prevents edge cases)
