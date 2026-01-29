# Spec: metaball-system

**File**: `specs/metaball-system/spec.md`

## 1.1 Purpose

Define the universal metaball system that provides organic fluid merging effects on all platforms with intelligent performance optimization, including SVG goo filter implementation, platform-aware blur, spring physics, blob limits, and graceful degradation.

## 1.2 Scope

**In Scope**:
- SVG goo filter implementation (`<filter id="goo">`)
- Platform-aware blur (16px desktop, 12px mobile)
- Spring physics (attraction, repulsion, viscosity)
- Blob limits (12 desktop, 6 mobile)
- Performance monitoring and auto-disable
- Graceful degradation to clean circles
- Z-index layering (layer.metaball: 1)

**Out of Scope**:
- Widget rendering (widgets provide position/radius)
- Motion animations (handled by Framer Motion)
- Layout system (anchor positions, mobile stack)
- Widget spawning logic (handled by LangGraph)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-MS-001 | Metaballs MUST use SVG goo filter (works on all platforms) | Must |
| FR-MS-002 | Blur MUST be platform-aware (16px desktop, 12px mobile) | Must |
| FR-MS-003 | Blob count MUST be limited (12 desktop, 6 mobile) | Must |
| FR-MS-004 | Physics MUST be simplified on mobile (attraction only) | Must |
| FR-MS-005 | System MUST auto-disable if FPS drops below 20 | Must |
| FR-MS-006 | Reduced motion preference MUST be respected | Must |
| FR-MS-007 | Graceful degradation MUST fall back to clean circles | Must |
| FR-MS-008 | Metaball layer MUST be at z-index 1 (above background, below widgets) | Must |
| FR-MS-009 | Physics MUST use spring model (attraction, repulsion, viscosity) | Must |
| FR-MS-010 | Metaball canvas MUST be pointer-events-none (doesn't block interactions) | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-MS-001 | Desktop MUST render at ≥60fps | Should |
| NFR-MS-002 | Mobile MUST render at ≥30fps | Should |
| NFR-MS-003 | GPU acceleration MUST be used (SVG filters are GPU-accelerated) | Should |
| NFR-MS-004 | Auto-disable threshold MUST be configurable (default: FPS <20) | Could |

## 1.4 Data Model

**Locked from LLD** (agentx_organic_ui_design_system.md:839-932):

```typescript
// Metaball Canvas Component
interface MetaballCanvasProps {
  widgets: Array<{
    id: string
    x: number
    y: number
    radius: number
  }>
}

// Physics State
interface WidgetPhysics {
  id: string
  x: number
  y: number
  vx: number  // velocity X
  vy: number  // velocity Y
  radius: number
  anchor: {
    x: number
    y: number
  }
}

// Metaball Config (from capability.getMetaballConfig())
interface MetaballConfig {
  enabled: boolean
  blur: number  // 16 (desktop) or 12 (mobile)
  maxBlobs: number  // 12 (desktop) or 6 (mobile)
  simplifyPhysics: boolean  // true on mobile
}
```

**SVG Goo Filter** (Locked):
```typescript
<filter id="goo">
  <feGaussianBlur in="SourceGraphic" stdDeviation={config.blur} result="blur" />
  <feColorMatrix in="blur" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 24 -10" />
</filter>
```

**Spring Physics** (Locked):
```typescript
// Constants from tokens.metaball
const ATTRACTION = 0.02  // Spring toward anchor
const REPULSION = 0.05   // Push away from other blobs
const VISCOSITY = 0.3    // Friction (0 = no friction, 1 = no movement)
const MAX_SPEED = 2      // Maximum velocity

// Physics update (per frame)
function updateWidgetPhysics(widget: WidgetPhysics, allWidgets: WidgetPhysics[], delta: number) {
  const config = capability.getMetaballConfig()

  // Spring toward anchor point (universal)
  const anchor = anchors[widget.anchor]
  const dx = anchor.x - widget.x
  const dy = anchor.y - widget.y
  widget.vx += dx * tokens.metaball.attraction
  widget.vy += dy * tokens.metaball.attraction

  // Repulsion (skip on mobile for performance)
  if (!config.simplifyPhysics) {
    allWidgets.forEach(other => {
      if (other.id === widget.id) return
      const dist = distance(widget, other)
      if (dist < 200) {
        const force = tokens.metaball.repulsion / dist
        widget.vx -= force * (other.x - widget.x)
        widget.vy -= force * (other.y - widget.y)
      }
    })
  }

  // Apply friction
  widget.vx *= (1 - tokens.metaball.viscosity)
  widget.vy *= (1 - tokens.metaball.viscosity)

  // Update position
  widget.x += widget.vx * delta
  widget.y += widget.vy * delta
}
```

## 1.5 API Contract

**Note**: This spec has no API contracts (frontend-only).

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-MS-001 | Metaballs MUST be disabled when `prefers-reduced-motion` is true | Runtime check |
| BR-MS-002 | Blob count MUST NOT exceed `config.maxBlobs` | Runtime check (`widgets.slice(0, config.maxBlobs)`) |
| BR-MS-003 | Physics MUST skip repulsion on mobile (`config.simplifyPhysics === true`) | Runtime check |
| BR-MS-004 | Auto-disable MUST trigger when FPS <20 for 3 consecutive seconds | Performance monitoring |
| BR-MS-005 | Disabled state MUST render clean circles (no blur filter) | Conditional rendering |
| BR-MS-006 | Metaball canvas MUST NOT block pointer events | CSS `pointer-events: none` |

## 1.7 Acceptance Criteria

- [ ] SVG goo filter renders metaball merging effect
- [ ] Platform-aware blur applied (16px desktop, 12px mobile)
- [ ] Blob limits enforced (12 desktop, 6 mobile)
- [ ] Physics simplified on mobile (no repulsion)
- [ ] Auto-disable triggers when FPS <20 for 3 consecutive seconds
- [ ] `prefers-reduced-motion` disables metaballs
- [ ] Graceful degradation to circles when disabled
- [ ] Metaball layer at z-index 1
- [ ] Pointer events don't block interactions
- [ ] Desktop renders ≥60fps with 12 blobs
- [ ] Mobile renders ≥30fps with 6 blobs
- [ ] Spring physics produce organic movement
- [ ] Blobs merge when within threshold distance
