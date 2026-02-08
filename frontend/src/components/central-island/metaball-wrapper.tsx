/**
 * Metaball wrapper component for Central Island.
 *
 * Applies SVG gooey filter to create organic cell merging effect.
 * All components inside this wrapper will have metaball behavior.
 *
 * @see openspec/changes/morphing-central-island/specs/metaball-merge-behavior
 */

'use client';

import { ReactNode } from 'react';

export interface MetaballWrapperProps {
  children: ReactNode;
  /** Blur amount for metaball effect (default: 16) */
  blur?: number;
  /** Filter ID (must be unique per instance) */
  id?: string;
}

/**
 * Metaball wrapper - creates gooey cell merging effect.
 *
 * Wraps children in SVG filter that applies gaussian blur + alpha threshold.
 * This creates the biological cell engulfing/merging effect.
 *
 * IMPORTANT: All children must be in the same coordinate space for
 * the metaball effect to work. They should all be absolutely positioned
 * within a relative container.
 */
export function MetaballWrapper({
  children,
  blur = 16,
  id = 'metaball-central-island',
}: MetaballWrapperProps) {
  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* SVG filter for metaball effect */}
      <svg style={{ position: 'absolute', width: 0, height: 0 }}>
        <defs>
          <filter id={id}>
            {/* Gaussian blur for soft edges */}
            <feGaussianBlur in="SourceGraphic" stdDeviation={blur} result="blur" />
            {/* Color matrix for alpha thresholding */}
            <feColorMatrix
              in="blur"
              mode="matrix"
              values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -7"
              result="goo"
            />
            {/* Composite for clean edges */}
            <feComposite in="SourceGraphic" in2="goo" operator="atop" />
          </filter>
        </defs>
      </svg>

      {/* Children with metaball filter applied */}
      <div
        style={{
          filter: `url(#${id})`,
          width: '100%',
          height: '100%',
          position: 'relative',
        }}
      >
        {children}
      </div>
    </div>
  );
}
