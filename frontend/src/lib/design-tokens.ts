/**
 * Design tokens for Real AgentX Organic UI (C008).
 *
 * Single source of truth for all design constants.
 * Locked from agentx_organic_ui_design_system.md
 *
 * @see agentx_organic_ui_design_system.md
 */

export const tokens = {
  color: {
    void: '#0A0A0A',           // Deep space background
    membrane: '#141414',        // Subtle borders
    enzyme: '#00D9FF',          // Cyan accent (single accent color)
    cell: '#1E1E1E',           // Card backgrounds
    nucleus: '#FFFFFF',        // Primary text
    cytoplasm: '#A0A0A0',      // Secondary text
    vacuole: '#666666',        // Muted text
    mitochondria: '#FF6B35',   // Action/warning
    ribosome: '#00D9FF',       // Enzyme (same)
    golgi: '#FFD700',          // Success
    lysosome: '#FF4757',       // Error
    endoplasmic: '#C792EA',    // Info
    microtubule: '#64FFDA',    // Success alt
    actin: '#82AAFF',          // Info alt
    myosin: '#FFCB6B',         // Warning alt
  },
  spacing: {
    atom: 4,
    molecule: 8,
    organelle: 16,
    cell: 24,
    tissue: 32,
    organ: 48,
    system: 64,
    organism: 96,
    voice: 72,            // Voice nucleus radius (mobile)
    voiceDesktop: 160,    // Voice nucleus radius (desktop)
  },
  metaball: {
    mobileBlur: 12,
    desktopBlur: 16,
    mobileMaxBlobs: 6,
    desktopMaxBlobs: 12,
    radius: {
      voice: 160,         // Desktop nucleus
      voiceMobile: 72,     // Mobile nucleus
    }
  },
  typography: {
    fontSize: {
      xs: '0.75rem',      // 12px
      sm: '0.875rem',     // 14px
      base: '1rem',       // 16px
      lg: '1.125rem',     // 18px
      xl: '1.25rem',      // 20px
      '2xl': '1.5rem',    // 24px
      '3xl': '1.875rem',  // 30px
      '4xl': '2.25rem',   // 36px
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  motion: {
    duration: {
      fast: 150,
      normal: 300,
      slow: 500,
    },
    easing: {
      default: 'cubic-bezier(0.4, 0, 0.2, 1)',
      in: 'cubic-bezier(0.4, 0, 1, 1)',
      out: 'cubic-bezier(0, 0, 0.2, 1)',
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    },
  },
} as const;

export type DesignTokens = typeof tokens;

/**
 * Motion presets for organic UI animations (C008).
 *
 * @see agentx_organic_ui_design_system.md
 */
export const motion = {
  mitosis: {
    duration: 800,
    easing: [0.16, 1, 0.3, 1] as const,
  },
  pulse: {
    duration: 2000,
    repeat: Infinity,
  },
  drift: {
    duration: 20000,
    repeat: Infinity,
  },
  merge: {
    duration: 600,
    easing: [0.4, 0, 0.2, 1] as const,
  },
  divide: {
    duration: 400,
    easing: [0.4, 0, 0.2, 1] as const,
  },
  flow: {
    duration: 300,
    easing: [0.4, 0, 0.2, 1] as const,
  },
  breathe: {
    duration: 4000,
    repeat: Infinity,
  },
  pulseFast: {
    duration: 1000,
    repeat: Infinity,
  },
  settle: {
    duration: 500,
    easing: [0.16, 1, 0.3, 1] as const,
  },
} as const;

export type MotionPresets = typeof motion;
