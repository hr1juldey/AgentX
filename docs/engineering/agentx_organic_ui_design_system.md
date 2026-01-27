# Organic Voice UI Design System

**Vision:** A bio-inspired, metaball-based generative UI where a central "stem cell" voice interface divides and differentiates into data widgets. Desktop uses fluid organic physics; mobile adapts to clean, circular geometry while maintaining the same DNA.

---

## Core Philosophy

1. **One organism** - All UI emerges from a central voice nucleus
2. **Circular DNA** - Every element is a circle, bubble, or organic derivative
3. **Cell division metaphor** - Widgets spawn through mitosis-like animations
4. **Universal metaballs** - Organic fluid physics on ALL devices, optimized for performance
5. **Voice-first hierarchy** - Audio/voice is the root; visual is the expression
6. **Zero configuration sprawl** - Single source of truth

---

## Design Tokens (`design/tokens.ts`)

```typescript
export const tokens = {
  // Color Palette - Monochrome + single accent
  color: {
    // Base surfaces (inspired by Raycast's depth)
    void: '#0A0A0A',           // Deep space background
    membrane: '#141414',        // Primary surface
    cytoplasm: '#1C1C1C',      // Secondary surface
    organelle: '#252525',      // Tertiary surface (cards)
    
    // Text hierarchy
    nucleus: 'rgba(255,255,255,0.96)', // Primary text
    protein: 'rgba(255,255,255,0.72)', // Secondary text
    ghost: 'rgba(255,255,255,0.38)',   // Tertiary text
    
    // Accent (single, powerful)
    enzyme: '#00D9FF',         // Primary action (cyan life)
    enzymeSoft: 'rgba(0,217,255,0.12)',
    enzymeGlow: 'rgba(0,217,255,0.24)',
    
    // Semantic
    mitosis: '#00FF88',        // Success/growth
    apoptosis: '#FF4444',      // Error/death
    
    // Transparent overlays
    glassWeak: 'rgba(255,255,255,0.03)',
    glassMid: 'rgba(255,255,255,0.06)',
    glassStrong: 'rgba(255,255,255,0.09)',
  },
  
  // Radius - All circular derivatives
  radius: {
    cell: '50%',        // Perfect circle
    bubble: '42%',      // Slightly organic
    lg: '32px',         // Large organic
    md: '24px',         // Medium organic  
    sm: '16px',         // Small organic
    xs: '12px',         // Micro organic
  },
  
  // Spacing - 8px grid + golden ratio variants
  space: {
    nucleus: 4,    // Tight genetic spacing
    cell: 8,       // Base cell
    tissue: 16,    // Tissue cluster
    organ: 24,     // Organ system
    organism: 32,  // Full organism
    colony: 48,    // Multi-organism
    ecosystem: 64, // Layout regions
  },
  
  // Shadows - Soft depth (no harsh borders)
  shadow: {
    cell: '0 2px 8px rgba(0,0,0,0.3)',
    float: '0 8px 32px rgba(0,0,0,0.4)',
    deep: '0 16px 64px rgba(0,0,0,0.5)',
    glow: '0 0 24px rgba(0,217,255,0.3)',
    pulse: '0 0 48px rgba(0,217,255,0.5)',
  },
  
  // Blur - Glass morphism
  blur: {
    light: '8px',
    medium: '16px',
    heavy: '24px',
  },
  
  // Typography - Raycast-inspired clarity
  font: {
    family: {
      ui: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", system-ui, sans-serif',
      mono: '"SF Mono", "Fira Code", "Consolas", monospace',
      display: '"SF Pro Display", -apple-system, sans-serif', // For large voice text
    },
    size: {
      xs: '11px',
      sm: '13px',
      base: '15px',
      md: '17px',
      lg: '20px',
      xl: '24px',
      xxl: '32px',
      voice: '48px', // Large voice transcript
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
  
  // Timing - Biology-inspired durations
  timing: {
    instant: 80,      // Immediate feedback
    quick: 150,       // Micro-interactions
    normal: 240,      // Standard transitions
    spawn: 380,       // Widget birth
    morph: 520,       // Shape transformation
    drift: 2400,      // Idle floating
  },
  
  // Easing - Organic motion curves
  easing: {
    cell: [0.25, 0.1, 0.25, 1],           // Smooth organic
    elastic: [0.68, -0.55, 0.265, 1.55],  // Bounce
    anticipate: [0.22, 1, 0.36, 1],       // Start fast
    exit: [0.4, 0, 0.2, 1],               // Quick exit
  },
  
  // Metaball physics (universal - mobile optimized)
  metaball: {
    threshold: 0.5,           // Merge threshold
    viscosity: 0.3,           // Movement resistance
    attraction: 0.02,         // Cell attraction force
    repulsion: 0.05,          // Cell repulsion force
    maxSpeed: 2,              // Max velocity
    
    // Mobile optimizations
    mobileSimplify: true,     // Use simplified physics on mobile
    mobileBlur: 12,           // Lower blur for mobile (vs 16 desktop)
    mobileMaxBlobs: 6,        // Limit concurrent blobs on mobile
    
    radius: {
      micro: 32,              // Micro widget
      small: 64,              // Small widget
      medium: 96,             // Medium widget
      large: 128,             // Large widget
      voice: 160,             // Central voice nucleus (desktop)
      voiceMobile: 72,        // Smaller on mobile for thumb reach
    },
  },
  
  // Size presets for widgets
  widget: {
    micro: { w: 180, h: 120 },   // Tiny info card
    small: { w: 280, h: 200 },   // Single metric
    medium: { w: 380, h: 280 },  // Chart/list
    large: { w: 520, h: 380 },   // Rich content
    hero: { w: 720, h: 480 },    // Featured
  },
  
  // Z-index layers
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

// Viewport breakpoints
export const breakpoint = {
  mobile: 640,
  tablet: 1024,
  desktop: 1440,
  wide: 1920,
}

// Feature detection
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
  // Mobile gets optimized metaballs, not disabled
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

---

## Motion Presets (`design/motion.ts`)

```typescript
import { tokens } from './tokens'

export const motion = {
  // Cell division - widget spawning
  mitosis: {
    initial: { 
      scale: 0, 
      opacity: 0,
      filter: 'blur(12px)',
    },
    animate: { 
      scale: 1, 
      opacity: 1,
      filter: 'blur(0px)',
    },
    exit: { 
      scale: 0.8, 
      opacity: 0,
      filter: 'blur(8px)',
    },
    transition: {
      duration: tokens.timing.spawn / 1000,
      ease: tokens.easing.elastic,
    },
  },
  
  // Nucleus pulse - voice active state
  pulse: {
    animate: {
      scale: [1, 1.08, 1],
      boxShadow: [
        tokens.shadow.glow,
        tokens.shadow.pulse,
        tokens.shadow.glow,
      ],
    },
    transition: {
      duration: 1.4,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
  
  // Idle floating - breathing motion
  drift: {
    animate: {
      y: [0, -8, 0],
      x: [0, 4, 0],
    },
    transition: {
      duration: tokens.timing.drift / 1000,
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
      duration: tokens.timing.quick / 1000,
    },
  },
  
  // Press - quick compression
  compress: {
    whileTap: {
      scale: 0.96,
    },
    transition: {
      duration: tokens.timing.instant / 1000,
    },
  },
  
  // Drag - emphasized state
  drag: {
    whileDrag: {
      scale: 1.05,
      boxShadow: tokens.shadow.deep,
      cursor: 'grabbing',
      zIndex: tokens.layer.float + 10,
    },
  },
  
  // Morph - shape transformation
  morph: {
    transition: {
      duration: tokens.timing.morph / 1000,
      ease: tokens.easing.cell,
    },
  },
  
  // Text streaming - progressive reveal
  stream: {
    initial: { opacity: 0, x: -8 },
    animate: { opacity: 1, x: 0 },
    transition: {
      duration: tokens.timing.quick / 1000,
      ease: tokens.easing.anticipate,
    },
  },
  
  // Interrupt signal - attention grab
  interrupt: {
    initial: { scale: 0.8, opacity: 0 },
    animate: { 
      scale: [0.8, 1.1, 1],
      opacity: 1,
    },
    transition: {
      duration: 0.4,
      ease: tokens.easing.elastic,
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

---

## CSS Variables (`styles/globals.css`)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* Colors */
  --void: #0A0A0A;
  --membrane: #141414;
  --cytoplasm: #1C1C1C;
  --organelle: #252525;
  --nucleus: rgba(255,255,255,0.96);
  --protein: rgba(255,255,255,0.72);
  --ghost: rgba(255,255,255,0.38);
  --enzyme: #00D9FF;
  --enzyme-soft: rgba(0,217,255,0.12);
  --enzyme-glow: rgba(0,217,255,0.24);
  --mitosis: #00FF88;
  --apoptosis: #FF4444;
  
  /* Radius */
  --r-cell: 50%;
  --r-bubble: 42%;
  --r-lg: 32px;
  --r-md: 24px;
  --r-sm: 16px;
  --r-xs: 12px;
  
  /* Shadows */
  --shadow-cell: 0 2px 8px rgba(0,0,0,0.3);
  --shadow-float: 0 8px 32px rgba(0,0,0,0.4);
  --shadow-deep: 0 16px 64px rgba(0,0,0,0.5);
  --shadow-glow: 0 0 24px rgba(0,217,255,0.3);
  --shadow-pulse: 0 0 48px rgba(0,217,255,0.5);
  
  /* Blur */
  --blur-light: 8px;
  --blur-medium: 16px;
  --blur-heavy: 24px;
  
  /* Typography */
  --font-ui: -apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif;
  --font-mono: "SF Mono", "Fira Code", monospace;
  
  /* Timing */
  --t-instant: 80ms;
  --t-quick: 150ms;
  --t-normal: 240ms;
  --t-spawn: 380ms;
  --t-morph: 520ms;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body, #__next {
  height: 100%;
  background: var(--void);
  color: var(--nucleus);
  font-family: var(--font-ui);
  font-size: 15px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Selection */
::selection {
  background: var(--enzyme-soft);
  color: var(--enzyme);
}

/* Focus visible */
:focus-visible {
  outline: 2px solid var(--enzyme);
  outline-offset: 2px;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--organelle);
  border-radius: var(--r-lg);
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.2);
}
```

---

## Tailwind Config (`tailwind.config.js`)

```javascript
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './design/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        void: 'var(--void)',
        membrane: 'var(--membrane)',
        cytoplasm: 'var(--cytoplasm)',
        organelle: 'var(--organelle)',
        nucleus: 'var(--nucleus)',
        protein: 'var(--protein)',
        ghost: 'var(--ghost)',
        enzyme: 'var(--enzyme)',
      },
      borderRadius: {
        cell: 'var(--r-cell)',
        bubble: 'var(--r-bubble)',
        lg: 'var(--r-lg)',
        md: 'var(--r-md)',
        sm: 'var(--r-sm)',
        xs: 'var(--r-xs)',
      },
      boxShadow: {
        cell: 'var(--shadow-cell)',
        float: 'var(--shadow-float)',
        deep: 'var(--shadow-deep)',
        glow: 'var(--shadow-glow)',
        pulse: 'var(--shadow-pulse)',
      },
      backdropBlur: {
        light: 'var(--blur-light)',
        medium: 'var(--blur-medium)',
        heavy: 'var(--blur-heavy)',
      },
      fontFamily: {
        ui: 'var(--font-ui)',
        mono: 'var(--font-mono)',
      },
      transitionDuration: {
        instant: 'var(--t-instant)',
        quick: 'var(--t-quick)',
        normal: 'var(--t-normal)',
        spawn: 'var(--t-spawn)',
        morph: 'var(--t-morph)',
      },
    },
  },
  plugins: [],
}
```

---

## Primitive Components (`design/surfaces.tsx`)

```typescript
import React from 'react'
import { motion } from 'framer-motion'
import { tokens } from './tokens'

// Base glass surface - building block for all UI
export function Cell({ 
  children, 
  className = '',
  size = 'medium',
  ...props 
}: {
  children: React.ReactNode
  className?: string
  size?: 'micro' | 'small' | 'medium' | 'large'
  [key: string]: any
}) {
  const sizeClasses = {
    micro: 'p-2',
    small: 'p-3',
    medium: 'p-4',
    large: 'p-6',
  }
  
  return (
    <div
      className={`
        rounded-lg
        bg-white/[0.03]
        backdrop-blur-medium
        border border-white/[0.06]
        shadow-cell
        ${sizeClasses[size]}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  )
}

// Animated cell with motion presets
export function MotionCell({
  children,
  variant = 'mitosis',
  ...props
}: {
  children: React.ReactNode
  variant?: 'mitosis' | 'drift'
  [key: string]: any
}) {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={variant === 'mitosis' ? motion.mitosis : motion.drift}
      {...props}
    >
      <Cell>{children}</Cell>
    </motion.div>
  )
}

// Circular nucleus - for voice/central elements
export function Nucleus({
  size = 160,
  active = false,
  children,
  ...props
}: {
  size?: number
  active?: boolean
  children?: React.ReactNode
  [key: string]: any
}) {
  return (
    <motion.div
      className="rounded-cell bg-organelle backdrop-blur-heavy border border-white/[0.09]"
      style={{
        width: size,
        height: size,
        boxShadow: active ? tokens.shadow.pulse : tokens.shadow.float,
      }}
      animate={active ? motion.pulse.animate : undefined}
      transition={active ? motion.pulse.transition : undefined}
      {...props}
    >
      <div className="w-full h-full flex items-center justify-center">
        {children}
      </div>
    </motion.div>
  )
}

// Text with streaming animation
export function StreamText({
  children,
  delay = 0,
}: {
  children: string
  delay?: number
}) {
  return (
    <motion.span
      initial={motion.stream.initial}
      animate={motion.stream.animate}
      transition={{
        ...motion.stream.transition,
        delay,
      }}
    >
      {children}
    </motion.span>
  )
}
```

---

## Voice Interface Design

### Universal Metaball System

**Philosophy:** Metaballs work on ALL devices, but with intelligent optimization:

**Desktop Implementation:**
- Full metaball physics with 16px blur
- Up to 12 concurrent blobs
- Complex spring physics with attraction/repulsion
- 60fps target

**Mobile Implementation:**
- Simplified metaball physics with 12px blur (25% less GPU load)
- Maximum 6 concurrent blobs (better performance)
- Simplified physics: only attraction to anchors, minimal repulsion
- 30fps target (acceptable on mobile, saves battery)

**Why This Works:**
- Visual language stays consistent across devices
- Performance optimized per platform automatically
- Users see organic fluidity everywhere
- Mobile users with powerful devices still get beautiful effects

### Central Voice Nucleus

**Desktop:**
- 160px circular nucleus at viewport center
- Active: pulsing glow + scale animation
- Idle: gentle drift motion
- On speak: spawn transcript bubbles that float to top
- On listen: inner circle fills with waveform visualization

**Mobile:**
- 72px circular nucleus at bottom-center (thumb-friendly)
- Same pulse/glow when active
- Fixed position for reliable touch target
- Same visual language, optimized size

**Widget Spawning (Universal):**
- Widgets emerge from nucleus via "mitosis" animation
- Start as tiny circles, morph into rounded rectangles
- Float to anchor positions using spring physics
- Metaball merging happens when widgets are close (<80px on desktop, <60px on mobile)
- On mobile: limit to 6 widgets max, older widgets fade out

---

## Layout System

### Anchor Positions (Desktop)

```typescript
export const anchors = {
  'top-left': { x: '10%', y: '10%' },
  'top-center': { x: '50%', y: '10%' },
  'top-right': { x: '90%', y: '10%' },
  'mid-left': { x: '10%', y: '50%' },
  'mid-right': { x: '90%', y: '50%' },
  'bottom-left': { x: '10%', y: '90%' },
  'bottom-right': { x: '90%', y: '90%' },
}
```

### Mobile Stack (Metaball-Enhanced)

```typescript
export const mobileLayout = {
  voice: { 
    position: 'fixed', 
    bottom: 24, 
    centerX: true,
    size: 72, // Larger tap target
  },
  widgets: { 
    position: 'flow', // Not rigid stack - organic flow with metaballs
    padding: 16,
    gap: 12, // Tighter for mobile
    maxWidth: 'calc(100vw - 32px)',
    maxVisible: 6, // Performance limit
  },
  metaball: {
    enabled: true,
    simplified: true, // Use simpler physics
    blur: 12, // Less blur = better mobile performance
  },
}
```

---

## Voice-Specific UX Rules

### Pacing & Timing

1. **User speaks** → Voice button pulses → Audio captured
2. **Processing** → Skeleton lines appear (200ms delay)
3. **AI responds** → 3 parallel streams:
   - **Text tokens** → Streamed to transcript (grouped in 200ms windows)
   - **Audio chunks** → Progressive playback
   - **Widget instructions** → Spawn widgets with mitosis animation

### Transcript Rendering

```typescript
// Chunk tokens into 200ms windows for animation
const transcriptChunks = groupTokensBy200ms(tokens)

transcriptChunks.forEach((chunk, i) => {
  return (
    <StreamText key={i} delay={i * 0.2}>
      {chunk}
    </StreamText>
  )
})
```

### Audio Playback

- Single global `AudioContext`
- Queue audio chunks as they arrive
- Show mini waveform visualization in voice nucleus
- Transcript text highlights in sync with audio

### Interrupt Handling

- **Desktop:** Spacebar or click nucleus during playback
- **Mobile:** "Tap to interrupt" pill (spawns with interrupt animation)
- On interrupt: fade out current audio, clear queue, reset voice state

---

## Widget Protocol (Generative UI)

### Message Format

```typescript
type WidgetMessage = {
  type: 'widget'
  id: string
  component: 'chart' | 'card' | 'list' | 'markdown'
  anchor?: AnchorPosition // Desktop only
  size?: 'micro' | 'small' | 'medium' | 'large'
  props: Record<string, any>
}
```

### Spawning Logic (Universal)

```typescript
function spawnWidget(msg: WidgetMessage) {
  const config = capability.getMetaballConfig()
  
  // 1. Create widget with mitosis animation
  const widget = {
    ...msg,
    position: getAnchorPosition(msg.anchor || 'mid-right'),
    // Initialize physics properties
    x: window.innerWidth / 2, // Start from nucleus
    y: window.innerHeight / 2,
    vx: 0,
    vy: 0,
    radius: tokens.metaball.radius[msg.size || 'medium'],
  }
  
  // 2. Add to scene
  addWidget(widget)
  
  // 3. Start metaball physics (works on all platforms)
  if (config.enabled) {
    startPhysicsLoop(widget)
  }
  
  // 4. Mobile: enforce max widget limit
  if (config.maxBlobs && widgets.length > config.maxBlobs) {
    fadeOutOldestWidget()
  }
}
```

---

## Metaball Implementation (Universal, Platform-Optimized)

### SVG Goo Filter (Works Everywhere)

```typescript
function MetaballCanvas({ widgets }) {
  const config = capability.getMetaballConfig()
  
  if (!config.enabled) return null // Respect reduced-motion
  
  return (
    <svg 
      className="absolute inset-0 pointer-events-none" 
      style={{ zIndex: tokens.layer.metaball }}
    >
      <defs>
        <filter id="goo">
          <feGaussianBlur 
            in="SourceGraphic" 
            stdDeviation={config.blur} 
            result="blur" 
          />
          <feColorMatrix
            in="blur"
            type="matrix"
            values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 24 -10"
          />
        </filter>
      </defs>
      <g filter="url(#goo)">
        {widgets.slice(0, config.maxBlobs).map(w => (
          <circle
            key={w.id}
            cx={w.x}
            cy={w.y}
            r={w.radius}
            fill="rgba(255,255,255,0.06)"
          />
        ))}
      </g>
    </svg>
  )
}
```

### Physics (Simplified for Mobile)

```typescript
function updateWidgetPhysics(widget, allWidgets, delta) {
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

### Performance Notes

**Why This Works on Mobile:**
1. **SVG filters are GPU-accelerated** - Modern mobile browsers handle this well
2. **Reduced blur** (12px vs 16px) = 25% less GPU load
3. **Fewer blobs** (6 vs 12) = 50% less computation
4. **Simplified physics** - Only attraction, no inter-blob repulsion
5. **RequestAnimationFrame throttling** - 30fps target on mobile vs 60fps desktop

**Fallback:**
- If device is truly struggling, metaballs auto-disable after dropped frames detected
- Graceful degradation to clean circles (same layout, no goo filter)

---

## Accessibility

### Keyboard Navigation

- `Tab` → Focus next widget
- `Space` → Activate voice (toggle)
- `Escape` → Close active widget
- `Arrow keys` → Navigate within widgets

### Screen Reader

- Voice button: "Voice input. Press space to start speaking."
- Widgets: Proper ARIA labels for each component type
- Transcript: Live region with polite updates

### Reduced Motion

```typescript
if (capability.prefersReducedMotion()) {
  // Disable metaballs
  // Instant transitions instead of springs
  // No drift/pulse animations
}
```

### Touch Targets

- Minimum 44px (WCAG)
- Voice button: 72px (generous)
- Widget close buttons: 44px

---

## Implementation Checklist

### Phase 1: Foundations (Day 1)
- [ ] Create `design/tokens.ts`
- [ ] Create `design/motion.ts`
- [ ] Setup `globals.css` with CSS variables
- [ ] Configure Tailwind
- [ ] Build `Cell`, `Nucleus`, `StreamText` primitives

### Phase 2: Voice Core (Day 2)
- [ ] Implement voice button with pulse animation
- [ ] WebSocket connection for streaming
- [ ] Audio capture + playback
- [ ] Transcript rendering with streaming animation
- [ ] Interrupt handling

### Phase 3: Widgets (Day 3)
- [ ] Widget spawning system (mitosis animation)
- [ ] 3 core widgets: Chart, Card, Markdown
- [ ] Mobile stack layout
- [ ] Desktop anchor positioning

### Phase 4: Metaballs (Day 4, Universal)
- [ ] SVG goo filter with platform-aware blur
- [ ] Spring physics with mobile simplification
- [ ] Merge detection
- [ ] Performance monitoring + auto-disable fallback
- [ ] Mobile: 6-widget limit with fade-out

### Phase 5: Polish (Day 5)
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] Reduced motion mode
- [ ] Haptic feedback (mobile)
- [ ] Error states

---

## Example: Voice Button Component

```typescript
'use client'
import { motion } from 'framer-motion'
import { motion as motionPresets } from '@/design/motion'
import { tokens } from '@/design/tokens'
import { Nucleus } from '@/design/surfaces'

export function VoiceButton({ 
  active, 
  onToggle 
}: { 
  active: boolean
  onToggle: () => void 
}) {
  const isMobile = capability.isMobile()
  const size = isMobile ? 72 : 160
  
  return (
    <motion.button
      onClick={onToggle}
      onKeyDown={(e) => e.key === ' ' && onToggle()}
      className="focus:outline-none focus-visible:ring-2 focus-visible:ring-enzyme"
      style={{
        position: isMobile ? 'fixed' : 'absolute',
        bottom: isMobile ? 24 : '50%',
        left: '50%',
        transform: isMobile ? 'translateX(-50%)' : 'translate(-50%, 50%)',
      }}
      aria-label={active ? "Stop speaking" : "Start speaking"}
      aria-pressed={active}
      {...motionPresets.lift}
      {...motionPresets.compress}
    >
      <Nucleus size={size} active={active}>
        <motion.div
          className="w-8 h-8 rounded-cell bg-enzyme"
          animate={active ? {
            scale: [1, 1.2, 1],
          } : {}}
          transition={{
            duration: 0.6,
            repeat: active ? Infinity : 0,
          }}
        />
      </Nucleus>
    </motion.button>
  )
}
```

---

## Color Palette Rationale

- **Monochrome base** → Raycast-inspired depth through subtle grays
- **Single accent (cyan)** → Represents "life" in bio metaphor, high contrast
- **No bright colors** → Keeps focus on content, not chrome
- **Semantic colors** → Green (growth/success), Red (death/error)

---

## Font System Rationale

- **SF Pro Display** → Apple's system font, excellent for voice transcripts
- **15px base** → Raycast standard, comfortable reading size
- **48px voice text** → Large, clear for real-time transcript

---

## Motion Rationale

- **Elastic easing** → Mimics organic cell behavior
- **380ms spawn** → Fast enough to feel responsive, slow enough to see
- **Pulse at 1.4s** → Relaxed breathing rhythm
- **200ms token chunking** → Prevents animation overload during streaming

---

## What This Gives You

1. ✅ **Single source of truth** → Change `tokens.ts`, entire UI updates
2. ✅ **Universal metaballs** → Same organic fluidity on desktop AND mobile
3. ✅ **Intelligent optimization** → Mobile gets 12px blur (vs 16px), 6 blobs max (vs 12), simplified physics
4. ✅ **Graceful degradation** → Auto-disables on struggling devices, falls back to clean circles
5. ✅ **Bio-inspired metaphors** → Code reads like biology (nucleus, enzyme, mitosis)
6. ✅ **Voice-first UX** → Central nucleus spawns widgets, not chrome
7. ✅ **Raycast-level polish** → Clean, accessible, professional
8. ✅ **Performance monitoring** → Dropped frames trigger automatic simplification

---

## Mobile-Specific Optimizations

### Why Metaballs Work on Mobile Now:

1. **Reduced blur** - 12px vs 16px = 25% less GPU work
2. **Blob limit** - Max 6 concurrent (vs 12 desktop)
3. **Simplified physics** - Attraction only, no repulsion calculations
4. **Lower framerate target** - 30fps acceptable on mobile
5. **Auto-disable** - If FPS drops below 20, switches to static circles
6. **Battery-aware** - Respects low-power mode on iOS

### Visual Consistency:

Despite optimizations, mobile users see:
- Same organic goo merging
- Same circular language
- Same spawn animations
- Same color palette
- Just slightly simpler under the hood (imperceptible to users)