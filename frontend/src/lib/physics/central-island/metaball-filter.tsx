/**
 * Metaball filter component for Central Island.
 *
 * Copied from physics-cells-voice and adapted for central-island use.
 * Uses SVG goo filter for organic cell merging effects.
 *
 * @see openspec/changes/morphing-central-island/specs/metaball-merge-behavior
 */

'use client';

import { useMemo } from 'react';

export interface MetaballFilterProps {
  /** Unique ID for this filter instance (required for multiple filters) */
  id: string;
  /** Blur amount for metaball effect (default: 16) */
  blur?: number;
  /** Color matrix values for alpha thresholding (default: "1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -7") */
  colorMatrix?: string;
}

/**
 * Metaball SVG filter component.
 *
 * Creates organic gooey merge effect when shapes overlap.
 * Use by wrapping shapes in a <g filter="url(#filter-id)"> element.
 */
export function MetaballFilter({
  id,
  blur = 16,
  colorMatrix = '1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -7',
}: MetaballFilterProps) {
  const filterId = `metaball-${id}`;

  return (
    <svg style={{ position: 'absolute', width: 0, height: 0 }}>
      <defs>
        <filter id={filterId}>
          {/* Gaussian blur for soft edges */}
          <feGaussianBlur in="SourceGraphic" stdDeviation={blur} result="blur" />
          {/* Color matrix for alpha thresholding */}
          <feColorMatrix in="blur" mode="matrix" values={colorMatrix} result="goo" />
          {/* Composite for clean edges */}
          <feComposite in="SourceGraphic" in2="goo" operator="atop" />
        </filter>
      </defs>
    </svg>
  );
}

/**
 * Hook to get the filter URL for use in style/filter attributes.
 */
export function useMetaballFilter(id: string): string {
  return useMemo(() => `url(#metaball-${id})`, [id]);
}
