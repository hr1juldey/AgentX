# Spec: design-tokens

**File**: `specs/design-tokens/spec.md`

## 1.1 Purpose

Define the single source of truth design token system that powers the entire Organic UI, providing frozen constants for colors, spacing, typography, shadows, blur, timing, easing, metaball physics, and platform-aware configurations.

## 1.2 Scope

**In Scope**:
- Design token definitions (color, radius, space, shadow, blur, font, timing, easing, metaball, widget, layer)
- Capability detection (isMobile, prefersReducedMotion, getMetaballConfig)
- Breakpoint definitions (mobile, tablet, desktop, wide)
- TypeScript token exports (`design/tokens.ts`)
- CSS variable generation (`globals.css`)
- Tailwind config extension (`tailwind.config.js`)

**Out of Scope**:
- Component implementations (Cell, Nucleus, VoiceButton)
- Motion preset implementations
- Metaball physics engine
- Widget spawning logic
- Layout system (anchors, mobile stack)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DT-001 | Design tokens MUST be defined in single TypeScript file (`design/tokens.ts`) | Must |
| FR-DT-002 | Token values MUST be frozen (no runtime modifications) | Must |
| FR-DT-003 | CSS variables MUST be auto-generated from tokens | Must |
| FR-DT-004 | Tailwind config MUST extend tokens (not duplicate values) | Must |
| FR-DT-005 | Capability detection MUST check viewport + UA + features (not just UA) | Must |
| FR-DT-006 | `getMetaballConfig()` MUST return platform-aware configuration | Must |
| FR-DT-007 | All token values MUST match LLD exactly (no deviations) | Must |
| FR-DT-008 | Token categories MUST include: color, radius, space, shadow, blur, font, timing, easing, metaball, widget, layer | Must |
| FR-DT-009 | Breakpoints MUST be defined as: mobile (640), tablet (1024), desktop (1440), wide (1920) | Must |
| FR-DT-010 | Capability functions MUST be SSR-safe (check for `window` before accessing) | Should |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-DT-001 | Token file MUST be under 200 lines | Should |
| NFR-DT-002 | Token access MUST be type-safe (TypeScript) | Must |
| NFR-DT-003 | CSS variables MUST follow CSS custom property syntax (`--token-name`) | Must |
| NFR-DT-004 | Tailwind extension MUST preserve token naming (camelCase → kebab-case) | Must |

## 1.4 Data Model

**Locked from LLD** (agentx_organic_ui_design_system.md:18-210):

```typescript
// design/tokens.ts
export const tokens = {
  color: {
    void: '#0A0A0A',
    membrane: '#141414',
    cytoplasm: '#1C1C1C',
    organelle: '#252525',
    nucleus: 'rgba(255,255,255,0.96)',
    protein: 'rgba(255,255,255,0.72)',
    ghost: 'rgba(255,255,255,0.38)',
    enzyme: '#00D9FF',
    enzymeSoft: 'rgba(0,217,255,0.12)',
    enzymeGlow: 'rgba(0,217,255,0.24)',
    mitosis: '#00FF88',
    apoptosis: '#FF4444',
    glassWeak: 'rgba(255,255,255,0.03)',
    glassMid: 'rgba(255,255,255,0.06)',
    glassStrong: 'rgba(255,255,255,0.09)',
  },
  radius: {
    cell: '50%',
    bubble: '42%',
    lg: '32px',
    md: '24px',
    sm: '16px',
    xs: '12px',
  },
  space: {
    nucleus: 4,
    cell: 8,
    tissue: 16,
    organ: 24,
    organism: 32,
    colony: 48,
    ecosystem: 64,
  },
  shadow: {
    cell: '0 2px 8px rgba(0,0,0,0.3)',
    float: '0 8px 32px rgba(0,0,0,0.4)',
    deep: '0 16px 64px rgba(0,0,0,0.5)',
    glow: '0 0 24px rgba(0,217,255,0.3)',
    pulse: '0 0 48px rgba(0,217,255,0.5)',
  },
  blur: {
    light: '8px',
    medium: '16px',
    heavy: '24px',
  },
  font: {
    family: {
      ui: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", system-ui, sans-serif',
      mono: '"SF Mono", "Fira Code", "Consolas", monospace',
      display: '"SF Pro Display", -apple-system, sans-serif',
    },
    size: {
      xs: '11px',
      sm: '13px',
      base: '15px',
      md: '17px',
      lg: '20px',
      xl: '24px',
      xxl: '32px',
      voice: '48px',
    },
    weight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    leading: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.7,
    },
  },
  timing: {
    instant: 80,
    quick: 150,
    normal: 240,
    spawn: 380,
    morph: 520,
    drift: 2400,
  },
  easing: {
    cell: [0.25, 0.1, 0.25, 1],
    elastic: [0.68, -0.55, 0.265, 1.55],
    anticipate: [0.22, 1, 0.36, 1],
    exit: [0.4, 0, 0.2, 1],
  },
  metaball: {
    threshold: 0.5,
    viscosity: 0.3,
    attraction: 0.02,
    repulsion: 0.05,
    maxSpeed: 2,
    mobileSimplify: true,
    mobileBlur: 12,
    mobileMaxBlobs: 6,
    radius: {
      micro: 32,
      small: 64,
      medium: 96,
      large: 128,
      voice: 160,
      voiceMobile: 72,
    },
  },
  widget: {
    micro: { w: 180, h: 120 },
    small: { w: 280, h: 200 },
    medium: { w: 380, h: 280 },
    large: { w: 520, h: 380 },
    hero: { w: 720, h: 480 },
  },
  layer: {
    bg: 0,
    metaball: 1,
    surface: 10,
    widget: 20,
    float: 30,
    voice: 40,
    modal: 50,
    toast: 60,
  },
}

export const breakpoint = {
  mobile: 640,
  tablet: 1024,
  desktop: 1440,
  wide: 1920,
}

export const capability = {
  isMobile: () => {
    if (typeof window === 'undefined') return false
    return window.innerWidth < breakpoint.tablet ||
           navigator.userAgent.match(/iPhone|iPad|Android/i)
  },
  prefersReducedMotion: () => {
    if (typeof window === 'undefined') return false
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches
  },
  getMetaballConfig: () => {
    const mobile = capability.isMobile()
    return {
      enabled: !capability.prefersReducedMotion(),
      blur: mobile ? tokens.metaball.mobileBlur : 16,
      maxBlobs: mobile ? tokens.metaball.mobileMaxBlobs : 12,
      simplifyPhysics: mobile,
    }
  },
}
```

## 1.5 API Contract

**Note**: This spec has no API contracts (frontend-only).

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-DT-001 | Token values MUST NOT be modified at runtime | TypeScript `as const` or `Object.freeze()` |
| BR-DT-002 | CSS variables MUST use kebab-case naming | Code review / Linter |
| BR-DT-003 | Tailwind config MUST reference CSS variables (not duplicate values) | Code review |
| BR-DT-004 | Capability detection MUST check `window` before accessing | TypeScript type guard |
| BR-DT-005 | All token colors MUST be valid CSS color values | Build-time validation |
| BR-DT-006 | All token sizes MUST be valid CSS units (px, %, rem, etc.) | Build-time validation |

## 1.7 Acceptance Criteria

- [ ] All token categories defined (color, radius, space, shadow, blur, font, timing, easing, metaball, widget, layer)
- [ ] Token file created at `design/tokens.ts`
- [ ] CSS variables generated in `globals.css`
- [ ] Tailwind config extends tokens (no duplication)
- [ ] `capability.isMobile()` checks viewport + UA + features
- [ ] `capability.getMetaballConfig()` returns platform-aware config
- [ ] Token values match LLD exactly (line-by-line verification)
- [ ] Token access is type-safe (TypeScript compilation)
- [ ] SSR-safe (checks for `window` before accessing)
- [ ] Token file under 200 lines
