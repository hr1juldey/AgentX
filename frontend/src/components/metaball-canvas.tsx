/**
 * Organic UI metaball background component (C008).
 *
 * Uses SVG goo filter for 2D metaballs with platform-aware optimization.
 * Mobile: 12px blur, max 6 blobs
 * Desktop: 16px blur, max 12 blobs
 *
 * @see agentx_organic_ui_design_system.md
 */

'use client';

import { useEffect, useState } from 'react';
import { tokens } from '@/lib/design-tokens';

interface Blob {
  id: number;
  x: number;
  y: number;
  r: number;
  vx: number;
  vy: number;
  color: string;
}

/**
 * Metaball background component with SVG goo filter.
 *
 * Creates organic, fluid background animation using SVG filter.
 * Platform-aware optimization for mobile devices.
 */
export function MetaballBackground() {
  const [blobs, setBlobs] = useState<Blob[]>([]);
  const [platform, setPlatform] = useState<'mobile' | 'desktop'>('desktop');

  // Detect platform
  useEffect(() => {
    const isMobile = /Mobile|Android|iPhone/i.test(navigator.userAgent);
    setPlatform(isMobile ? 'mobile' : 'desktop');
  }, []);

  // Initialize blobs
  useEffect(() => {
    const maxBlobs = platform === 'mobile'
      ? tokens.metaball.mobileMaxBlobs
      : tokens.metaball.desktopMaxBlobs;

    const newBlobs: Blob[] = [];
    const colors = [
      tokens.color.enzyme,
      tokens.color.actin,
      tokens.color.microtubule,
      tokens.color.endoplasmic,
    ];

    for (let i = 0; i < maxBlobs; i++) {
      newBlobs.push({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        r: 30 + Math.random() * 50,
        vx: (Math.random() - 0.5) * 0.2,
        vy: (Math.random() - 0.5) * 0.2,
        color: colors[Math.floor(Math.random() * colors.length)],
      });
    }

    setBlobs(newBlobs);
  }, [platform]);

  // Animate blobs
  useEffect(() => {
    if (blobs.length === 0) return;

    const animation = requestAnimationFrame(function animate() {
      setBlobs((prev) => {
        return prev.map((blob) => {
          let x = blob.x + blob.vx;
          let y = blob.y + blob.vy;
          let vx = blob.vx;
          let vy = blob.vy;

          // Bounce off edges
          if (x < 0 || x > 100) vx *= -1;
          if (y < 0 || y > 100) vy *= -1;

          x = Math.max(0, Math.min(100, x));
          y = Math.max(0, Math.min(100, y));

          return { ...blob, x, y, vx, vy };
        });
      });

      requestAnimationFrame(animate);
    });

    return () => cancelAnimationFrame(animation);
  }, [blobs.length]);

  const blur = platform === 'mobile'
    ? tokens.metaball.mobileBlur
    : tokens.metaball.desktopBlur;

  return (
    <svg
      className="absolute inset-0 w-full h-full -z-10 opacity-30"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        {/* SVG goo filter */}
        <filter id="goo">
          <feGaussianBlur in="SourceGraphic" stdDeviation={blur} result="blur" />
          <feColorMatrix
            in="blur"
            mode="matrix"
            values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7"
            result="goo"
          />
        </filter>
      </defs>

      {/* Blob circles with goo filter */}
      <g filter="url(#goo)">
        {blobs.map((blob) => (
          <circle
            key={blob.id}
            cx={`${blob.x}%`}
            cy={`${blob.y}%`}
            r={blob.r}
            fill={blob.color}
            opacity={0.6}
          />
        ))}
      </g>
    </svg>
  );
}
