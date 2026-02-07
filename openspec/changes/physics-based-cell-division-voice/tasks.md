# Tasks: Physics-Based Cell Division Voice Component

Implementation tasks organized by dependency order. Each task is verifiable and completable in one session.

---

## 1. Project Setup & Types

- [ ] 1.1 Create `frontend/src/types/library.ts` with `LibraryComponent` and `ComponentCategory` interfaces
- [ ] 1.2 Create `frontend/src/lib/navigation/library-routes.ts` with route constants (`ROUTES.LIBRARY`, `ROUTES.PHYSICS_CELLS`)
- [ ] 1.3 Create `frontend/src/lib/physics/` directory structure for physics modules

---

## 2. Physics Engine Implementation

### 2.1 Energy Accumulator

- [ ] 2.1.1 Create `frontend/src/lib/physics/energy-accumulator.ts`
- [ ] 2.1.2 Implement `updateEnergy(currentEnergy, audioLevel)` function with accumulation and decay
- [ ] 2.1.3 Add energy clamping to [0.0, 1.0] range
- [ ] 2.1.4 Export configuration types: `EnergyConfig { gainRate, decayRate }`

### 2.2 Spring Damping

- [ ] 2.2.1 Create `frontend/src/lib/physics/spring-damping.ts`
- [ ] 2.2.2 Implement `springDamped(target, current, stiffness)` returning velocity
- [ ] 2.2.3 Add `applyDamping(velocity, dampingFactor)` function
- [ ] 2.2.4 Export `SpringConfig { stiffness, damping }` type

### 2.3 Orbit Physics

- [ ] 2.3.1 Create `frontend/src/lib/physics/orbit-physics.ts`
- [ ] 2.3.2 Define `OrbitingCell` interface with `{ id, angle, distance, velocity, speed, baseDistance, radius, color }`
- [ ] 2.3.3 Implement `initializeCells(count)` returning distributed cell array
- [ ] 2.3.4 Implement `updateCell(cell, energy)` applying orbit mechanics and spring physics
- [ ] 2.3.5 Implement `polarToCartesian(angle, distance, radius)` conversion
- [ ] 2.3.6 Add nucleus counter-rotation calculation

### 2.4 Physics Hook

- [ ] 2.4.1 Create `frontend/src/lib/physics/usePhysicsCells.ts` React hook
- [ ] 2.4.2 Integrate energy accumulator, spring damping, and orbit physics
- [ ] 2.4.3 Implement `requestAnimationFrame` loop for 60 FPS updates
- [ ] 2.4.4 Return `{ cells, energy, start, stop }` API

---

## 3. Library Infrastructure

### 3.1 Routing Structure

- [ ] 3.1.1 Create `frontend/src/app/library/page.tsx` (library index)
- [ ] 3.1.2 Create `frontend/src/app/library/physics-cells/page.tsx` (component demo)
- [ ] 3.1.3 Verify routes work: navigate to `/library` and `/library/physics-cells`

### 3.2 Library Header

- [ ] 3.2.1 Create `frontend/src/components/layout/library-header.tsx`
- [ ] 3.2.2 Implement back button with route detection (`usePathname()`)
- [ ] 3.2.3 Add theme toggle button with localStorage persistence
- [ ] 3.2.4 Style header with fixed positioning and shadow

### 3.3 Root Layout Integration

- [ ] 3.3.1 Modify `frontend/src/app/layout.tsx` to add "Design Library" button to main header
- [ ] 3.3.2 Integrate `LibraryHeader` on library routes (route-specific layout if needed)

---

## 4. Main Component Implementation

### 4.1 Physics Cells Voice Component

- [ ] 4.1.1 Create `frontend/src/components/physics-cells-voice.tsx`
- [ ] 4.1.2 Implement SVG with metaball filter (`feGaussianBlur` + `feColorMatrix`)
- [ ] 4.1.3 Render nucleus circle at center (0, 0)
- [ ] 4.1.4 Render orbiting cells using `usePhysicsCells` hook
- [ ] 4.1.5 Implement dynamic viewBox sizing based on maxDistance + blur padding
- [ ] 4.1.6 Add responsive sizing (desktop: 160px nucleus, mobile: 72px)
- [ ] 4.1.7 Add cell breathing animation (sine wave radius scaling)

### 4.2 Audio Integration

- [ ] 4.2.1 Add Web Audio API `AnalyserNode` setup
- [ ] 4.2.2 Implement `getByteFrequencyData()` to extract audio level
- [ ] 4.2.3 Pass audio level to energy accumulator each frame
- [ ] 4.2.4 Handle microphone permissions gracefully
- [ ] 4.2.5 Add "Enable Mic" button for demo page

---

## 5. Demo Page Components

### 5.1 Component Card

- [ ] 5.1.1 Create `frontend/src/components/library/component-card.tsx`
- [ ] 5.1.2 Implement card layout: thumbnail, title, description, "View Demo →" button
- [ ] 5.1.3 Add hover effects (shadow elevation, button background)
- [ ] 5.1.4 Wrap with Next.js `<Link>` for client-side navigation

### 5.2 Demo Container

- [ ] 5.2.1 Create `frontend/src/components/library/demo-container.tsx`
- [ ] 5.2.2 Implement full-viewport demo area (~70-80% height)
- [ ] 5.2.3 Add description section with component title and explanation
- [ ] 5.2.4 Add control panel for component configuration (sliders, toggles)
- [ ] 5.2.5 Wrap component in error boundary for graceful error handling

### 5.3 Library Index Page

- [ ] 5.3.1 Implement `frontend/src/app/library/page.tsx` grid layout
- [ ] 5.3.2 Create component metadata array with physics cells entry
- [ ] 5.3.3 Map components to `<ComponentCard>` grid
- [ ] 5.3.4 Add responsive breakpoints (1 col mobile, 2 col tablet, 3 col desktop)
- [ ] 5.3.5 Add empty state handling ("No components yet")

### 5.4 Physics Cells Demo Page

- [ ] 5.4.1 Implement `frontend/src/app/library/physics-cells/page.tsx`
- [ ] 5.4.2 Use `<DemoContainer>` with `<PhysicsCellsVoice>` component
- [ ] 5.4.3 Add component description explaining audio-reactive behavior
- [ ] 5.4.4 Add controls: cell count slider [4-12], blur slider, enable mic button
- [ ] 5.4.5 Add debug mode showing energy bar and velocity values

---

## 6. Component Isolation

- [ ] 6.1 Verify each demo page creates fresh component instance on mount
- [ ] 6.2 Verify cleanup on unmount (audio context stop, timers cleared)
- [ ] 6.3 Verify no shared state between demo pages
- [ ] 6.4 Verify no global state usage (localStorage only for theme preference)

---

## 7. Visual Polish

- [ ] 7.1 Verify metaball merge behavior at distance < 0.25 (blur threshold)
- [ ] 7.2 Verify cell split behavior at distance > 0.50
- [ ] 7.3 Verify smooth 60 FPS animation (no frame drops)
- [ ] 7.4 Verify color scheme matches design tokens (purple accent)
- [ ] 7.5 Verify dark mode compatibility

---

## 8. Testing & Quality

- [ ] 8.1 Test navigation flow: main → library → physics-cells → back to library
- [ ] 8.2 Test browser back/forward button support
- [ ] 8.3 Test responsive sizing (mobile, tablet, desktop)
- [ ] 8.4 Test microphone permission grant/deny scenarios
- [ ] 8.5 Test component isolation (open multiple tabs, verify no interference)
- [ ] 8.6 Run `ruff check --fix` and `ruff format` on frontend code
- [ ] 8.7 Test all controls in demo page (cell count, blur, mic toggle)

---

## 9. Documentation

- [ ] 9.1 Add JSDoc comments to physics utility functions
- [ ] 9.2 Document component props API
- [ ] 9.3 Create thumbnail image for physics cells card (`/public/library/thumbnails/physics-cells.png` or `.webp`)
- [ ] 9.4 Update CLAUDE.md if any new project-wide patterns are introduced

---

## 10. Verification (Post-Implementation)

- [ ] 10.1 Run `/opsx:verify physics-based-cell-division-voice` to check implementation against specs
- [ ] 10.2 Address any CRITICAL issues found in verification
- [ ] 10.3 Review WARNING issues and address if applicable
- [ ] 10.4 Ensure all 10 specs have corresponding implementation

---

## Task Summary

**Total Tasks**: 75
**Physics Engine**: 14 tasks
**Library Infrastructure**: 8 tasks
**Main Component**: 12 tasks
**Demo Pages**: 20 tasks
**Isolation**: 4 tasks
**Polish**: 5 tasks
**Testing**: 7 tasks
**Documentation**: 4 tasks
**Verification**: 1 task

**Estimated Implementation Order**:
1. Setup & Types (3 tasks)
2. Physics Engine (14 tasks)
3. Library Infrastructure (8 tasks)
4. Main Component (12 tasks)
5. Demo Pages (20 tasks)
6. Isolation + Polish + Testing + Docs (20 tasks)
7. Verification (1 task)

**Definition of Done**: All tasks complete, `/opsx:verify` passes with no CRITICAL issues.
