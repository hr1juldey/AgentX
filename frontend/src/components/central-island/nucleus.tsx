/**
 * Nucleus component for Morphing Central Island.
 *
 * The primary interaction point - a living, breathing circular button
 * that stays idle until longpress, then reveals 4 mode islands.
 *
 * Uses physics-cells color scheme variables for consistency.
 * Draggable with spring physics when idle.
 *
 * @see openspec/changes/morphing-central-island/specs/nucleus-idle-state
 */

'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { ColorSchemeType } from './mode-islands';

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
  /** Selected mode (for color display and collapse target) */
  selectedMode?: 'voice' | 'chat' | 'file' | 'camera' | null;
  /** Whether collapse is active (for pulse and position animation) */
  isCollapsing?: boolean;
  /** Collapse progress for pulse timing */
  collapseProgress?: number;
  /** Whether collapse is complete (nucleus absorbed) */
  collapseComplete?: boolean;
  /** Current position of selected mode (for collapse target) */
  selectedModeCurrentPosition?: { x: number; y: number } | null;
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
  selectedMode,
  isCollapsing = false,
  collapseProgress = 0,
  collapseComplete = false,
  selectedModeCurrentPosition = null,
}: NucleusProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isPressed, setIsPressed] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  // Mode colors and positions from physics-cells scheme
  const modeColors = {
    voice: 'var(--scheme-cell-3, #A78BFA)',
    chat: 'var(--scheme-cell-2, #6366F1)',
    file: 'var(--scheme-cell-1, #22D3EE)',
    camera: 'var(--scheme-cell-5, #EC4899)',
  };

  const modePositions = {
    voice: { x: 0, y: -80 },
    chat: { x: -80, y: 0 },
    file: { x: 80, y: 0 },
    camera: { x: 0, y: 80 },
  };

  // Get nucleus color based on state and selected mode
  const getNucleusColor = () => {
    if (state === 'mode-selected' && selectedMode) {
      // Show selected mode's color
      return modeColors[selectedMode];
    }
    // Use CSS variables from color scheme - fallback to 'ai' scheme colors
    const inactiveColor = 'var(--scheme-nucleus-inactive, #22D3EE)';
    return inactiveColor;
  };

  // Calculate nucleus position (slides toward selected island during collapse)
  const getNucleusPosition = () => {
    // Start from center (0, 0)
    let posX = dragOffset.x;
    let posY = dragOffset.y;

    if (isCollapsing && selectedMode) {
      // Slide toward selected island's CURRENT position (where user dragged it)
      // Use provided current position if available, otherwise fall back to original position
      const targetPos = selectedModeCurrentPosition || modePositions[selectedMode];
      const progress = Math.min(1, collapseProgress * 1.5);
      posX = 0 + (targetPos.x - 0) * progress;
      posY = 0 + (targetPos.y - 0) * progress;

      console.log(`[Nucleus] Collapsing toward ${selectedMode} at (${targetPos.x.toFixed(0)}, ${targetPos.y.toFixed(0)}), progress=${progress.toFixed(2)}, my pos=(${posX.toFixed(0)}, ${posY.toFixed(0)})`);
    }

    return { x: posX, y: posY };
  };

  // Calculate nucleus scale (pulse during collapse, scales down when complete)
  const getNucleusScale = () => {
    if (collapseComplete) {
      // Nucleus absorbed - scale down to 0
      return 0;
    }
    if (isCollapsing && collapseProgress > 0) {
      // Pulse when absorbing: scale 1 → 1.15 → 1
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
      className="relative flex items-center justify-center rounded-full"
      style={{
        width: '60px',
        height: '60px',
        backgroundColor: getNucleusColor(),
        position: 'absolute', // Changed from 'fixed' to 'absolute' for container positioning
        top: '50%', // Center vertically
        left: '50%', // Center horizontally
        marginLeft: nucleusPosition.x, // Apply X offset during collapse/drag
        marginTop: nucleusPosition.y, // Apply Y offset during collapse/drag
        transform: 'translate(-50%, -50%)', // Offset by half width/height
        boxShadow: isPressed ? '0 2px 8px rgba(0, 0, 0, 0.15)' : '0 4px 12px rgba(0, 0, 0, 0.15)',
        cursor: (isCollapsing || collapseComplete) ? 'default' : 'pointer',
        border: 'none',
        outline: 'none',
        opacity: getNucleusOpacity(),
      }}
      animate={{
        scale: getNucleusScale(),
      }}
      transition={{
        type: 'spring',
        stiffness: 400,
        damping: 20,
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
