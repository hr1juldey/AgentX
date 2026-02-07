/**
 * Color scheme wrapper for physics cells demo.
 *
 * Applies Raycast-inspired color schemes using inline styles.
 * This ensures colors reach the SVG component reliably.
 */

'use client';

import { ReactNode } from 'react';

export interface ColorSchemeWrapperProps {
  scheme: string;
  children: ReactNode;
}

/**
 * Color scheme definitions with inline styles.
 */
const SCHEMES: Record<string, { vars: Record<string, string>; bg: string }> = {
  raycast: {
    vars: {
      '--scheme-cell-1': '#4F8CFF',
      '--scheme-cell-2': '#7C5CFF',
      '--scheme-cell-3': '#A855F7',
      '--scheme-cell-4': '#8B5CF6',
      '--scheme-cell-5': '#6366F1',
      '--scheme-cell-6': '#4F46E5',
      '--scheme-nucleus-active': '#7C5CFF',
      '--scheme-nucleus-inactive': '#4F8CFF',
    },
    bg: '#0B0B0C',
  },
  ai: {
    vars: {
      '--scheme-cell-1': '#22D3EE',
      '--scheme-cell-2': '#6366F1',
      '--scheme-cell-3': '#A78BFA',
      '--scheme-cell-4': '#8B5CF6',
      '--scheme-cell-5': '#EC4899',
      '--scheme-cell-6': '#F472B6',
      '--scheme-nucleus-active': '#6366F1',
      '--scheme-nucleus-inactive': '#22D3EE',
    },
    bg: '#0F1115',
  },
  warm: {
    vars: {
      '--scheme-cell-1': '#FF7A18',
      '--scheme-cell-2': '#FF3CAC',
      '--scheme-cell-3': '#784BA0',
      '--scheme-cell-4': '#9333EA',
      '--scheme-cell-5': '#C026D3',
      '--scheme-cell-6': '#DB2777',
      '--scheme-nucleus-active': '#FF3CAC',
      '--scheme-nucleus-inactive': '#FF7A18',
    },
    bg: '#0D0D0E',
  },
  minimal: {
    vars: {
      '--scheme-cell-1': '#4F46E5',
      '--scheme-cell-2': '#5B54F0',
      '--scheme-cell-3': '#6366F1',
      '--scheme-cell-4': '#6D74F5',
      '--scheme-cell-5': '#7882FF',
      '--scheme-cell-6': '#818CF8',
      '--scheme-nucleus-active': '#6366F1',
      '--scheme-nucleus-inactive': '#4F46E5',
    },
    bg: '#111113',
  },
  custom: {
    vars: {
      '--scheme-cell-1': '#00D9FF',
      '--scheme-cell-2': '#64FFDA',
      '--scheme-cell-3': '#82AAFF',
      '--scheme-cell-4': '#FFCB6B',
      '--scheme-cell-5': '#FFD700',
      '--scheme-cell-6': '#C792EA',
      '--scheme-nucleus-active': '#00D9FF',
      '--scheme-nucleus-inactive': '#FF6B35',
    },
    bg: '#0B0B0C',
  },
};

/**
 * Color scheme wrapper that applies CSS variables via inline styles.
 */
export function ColorSchemeWrapper({ scheme, children }: ColorSchemeWrapperProps) {
  const schemeConfig = SCHEMES[scheme] || SCHEMES.custom;

  return (
    <div
      className={`scheme-${scheme}`}
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: schemeConfig.bg,
        ...schemeConfig.vars,
      }}
    >
      {children}
    </div>
  );
}
