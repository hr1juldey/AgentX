/**
 * Nucleus component for Morphing Central Island.
 *
 * The primary interaction point - a living, breathing circular button
 * that stays idle until longpress, then reveals 4 mode islands.
 *
 * Uses physics-cells color scheme variables for consistency.
 * Draggable with spring physics when idle.
 *
 * Uses Zustand store for state management to sync with ModeIslands.
 *
 * @see openspec/changes/morphing-central-island/specs/nucleus-idle-state
 */

'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { useMorphingIslandStore, type ModeType } from './store';

export type ColorSchemeType = 'raycast' | 'ai' | 'warm' | 'minimal' | 'custom';

export interface NucleusProps {
  /** Current nucleus state for attribute tracking */
  state?: 'idle' | 'longpress' | 'mode-selected';
  /** Optional click handler (will integrate with longpress later) */
  onClick?: () => void;
  /** Optional children (for mode icons when active) */
  children?: React.ReactNode;
  /** Enable/disable hover effects */
  interactive?: boolean;
  /** Color scheme from physics-cells (default: 'ai') */
  colorScheme?: ColorSchemeType;
  /** Longpress handlers from useLongpress hook */
  onMouseDown?: (e: React.MouseEvent) => void;
  onMouseUp?: () => void;
  onMouseLeave?: () => void;
  onTouchStart?: (e: React.TouchEvent) => void;
  onTouchEnd?: () => void;
  /** Collapse progress for pulse timing */
  collapseProgress?: number;
}

/**
 * Nucleus - Central living button of the morphing UI.
 *
 * Features organic breathing animation (3s = 20bpm calm pulse),
 * responsive hover states, draggable behavior, and clean state tracking.
 * Uses physics-cells color scheme for visual consistency.
 *
 * During collapse: Nucleus slides toward selected island and merges with it.
 * After collapse complete: Nucleus is absorbed into selected island.
 *
 * Uses Zustand store for sync with ModeIslands state.
 */
export function Nucleus({
  state = 'idle',
  onClick,
  children,
  interactive = true,
  colorScheme = 'ai',
  onMouseDown,
  onMouseUp,
  onMouseLeave,
  onTouchStart,
  onTouchEnd,
  collapseProgress = 0,
}: NucleusProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isPressed, setIsPressed] = useState(false);

  // Get collapse state from store
  const selectedMode = useMorphingIslandStore((state) => state.selectedMode);
  const isCollapsing = useMorphingIslandStore((state) => state.isCollapsing);
  const collapseComplete = useMorphingIslandStore((state) => state.collapseComplete);
  const collapseIslandsCount = useMorphingIslandStore((state) => state.collapseIslandsCount);
  const getSelectedModeCurrentPosition = useMorphingIslandStore((state) => state.getSelectedModeCurrentPosition);

  // Mode colors from physics-cells scheme
  const modeColors: Record<ModeType, string> = {
    voice: 'var(--scheme-cell-3, #A78BFA)',
    chat: 'var(--scheme-cell-2, #6366F1)',
    file: 'var(--scheme-cell-1, #22D3EE)',
    camera: 'var(--scheme-cell-5, #EC4899)',
  };

  // Get nucleus color based on state and selected mode
  const getNucleusColor = () => {
    if (state === 'mode-selected' && selectedMode) {
      return modeColors[selectedMode];
    }
    return 'var(--scheme-nucleus-inactive, #22D3EE)';
  };

  // Calculate nucleus position (slides toward selected island during collapse)
  // SEQUENTIAL: Nucleus moves AFTER all islands have collapsed
  const getNucleusPosition = () => {
    // Start from center (0, 0)
    let posX = 0;
    let posY = 0;

    if (isCollapsing && selectedMode) {
      // Use the position that was captured when mode was selected (from store)
      const targetPos = getSelectedModeCurrentPosition();
      if (targetPos) {
        // Nucleus waits for islands to collapse first
        // Islands collapse in Phase 1 (progress 0-1), nucleus moves at the END
        const overallProgress = Math.min(1, collapseProgress * 1.5);

        // Nucleus moves only in the last portion of Phase 1 (after islands are done)
        // If there are 3 islands, each gets 1/3 of progress. Nucleus moves in the final 1/3.
        const islandCollapsePortion = Math.min(1, collapseIslandsCount / 4); // Islands get most of the time
        const nucleusMoveStart = islandCollapsePortion; // Nucleus starts after islands

        if (overallProgress >= nucleusMoveStart) {
          // Calculate nucleus movement progress
          const nucleusProgress = (overallProgress - nucleusMoveStart) / (1 - nucleusMoveStart);
          const clampedProgress = Math.min(1, nucleusProgress);

          posX = 0 + (targetPos.x - 0) * clampedProgress;
          posY = 0 + (targetPos.y - 0) * clampedProgress;

          console.log(`[Nucleus] Moving toward ${selectedMode} at (${targetPos.x.toFixed(0)}, ${targetPos.y.toFixed(0)}), nucleusProgress=${clampedProgress.toFixed(2)}, my pos=(${posX.toFixed(0)}, ${posY.toFixed(0)})`);
        } else {
          console.log(`[Nucleus] Waiting for islands... overall=${overallProgress.toFixed(2)}, start at=${nucleusMoveStart.toFixed(2)}`);
        }
      }
    }

    return { x: posX, y: posY };
  };

  // Calculate nucleus scale (pulse during collapse, scales down when complete)
  const getNucleusScale = () => {
    if (collapseComplete) {
      return 0;
    }
    if (isCollapsing && collapseProgress > 0) {
      const pulse = 1 + Math.sin(collapseProgress * Math.PI) * 0.15;
      return pulse;
    }
    return isPressed ? 0.98 : isHovered ? 1.08 : 1;
  };

  // Calculate nucleus opacity (fades out when absorbed)
  const getNucleusOpacity = () => {
    if (collapseComplete) {
      return 0;
    }
    return 1;
  };

  // Combine hover/pressed state with longpress handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (interactive && !isCollapsing && !collapseComplete) {
      setIsPressed(true);
      onMouseDown?.(e);
    }
  };

  const handleMouseUp = () => {
    setIsPressed(false);
    onMouseUp?.();
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    setIsPressed(false);
    onMouseLeave?.();
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    if (interactive && !isCollapsing && !collapseComplete) {
      setIsPressed(true);
      onTouchStart?.(e);
    }
  };

  const handleTouchEnd = () => {
    setIsPressed(false);
    onTouchEnd?.();
  };

  const nucleusPosition = getNucleusPosition();

  return (
    <motion.button
      data-nucleus-state={state}
      data-color-scheme={colorScheme}
      onClick={onClick}
      onMouseEnter={() => interactive && !isCollapsing && !collapseComplete && setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      className="absolute top-1/2 left-1/2 flex items-center justify-center rounded-full"
      style={{
        width: '60px',
        height: '60px',
        backgroundColor: getNucleusColor(),
        boxShadow: isPressed ? '0 2px 8px rgba(0, 0, 0, 0.15)' : '0 4px 12px rgba(0, 0, 0, 0.15)',
        cursor: (isCollapsing || collapseComplete) ? 'default' : 'pointer',
        border: 'none',
        outline: 'none',
      }}
      // Animate position with Framer Motion for smooth movement
      initial={{ x: 0, y: 0 }}
      animate={{
        x: nucleusPosition.x,
        y: nucleusPosition.y,
        scale: getNucleusScale(),
        opacity: getNucleusOpacity(),
      }}
      transition={{
        type: 'spring',
        stiffness: 400,
        damping: 20,
        // Smooth position transitions during collapse
        x: { type: 'spring', stiffness: 150, damping: 20 },
        y: { type: 'spring', stiffness: 150, damping: 20 },
      }}
    >
      {/* Breathing pulse animation - only visible in idle state */}
      {state === 'idle' && !isCollapsing && !collapseComplete && (
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{
            backgroundColor: getNucleusColor(),
            opacity: 0.3,
          }}
          animate={{
            scale: [1, 1.05, 1],
          }}
          transition={{
            duration: 3,
            ease: [0.4, 0, 0.6, 1], // cubic-bezier(0.4, 0, 0.6, 1)
            repeat: Infinity,
          }}
        />
      )}

      {/* Content (mode icons, etc.) */}
      <div className="relative z-10 flex items-center justify-center">
        {children}
      </div>
    </motion.button>
  );
}
