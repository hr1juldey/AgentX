/**
 * Sequential Collapse component for Morphing Central Island.
 *
 * Animates non-selected islands sliding toward and merging with
 * the selected island via metaball effect (cell engulfing).
 *
 * @see openspec/changes/morphing-central-island/specs/sequential-collapse
 */

'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export type ModeType = 'voice' | 'chat' | 'file' | 'camera';

export interface SequentialCollapseProps {
  /** Which mode was selected */
  selectedMode: ModeType | null;
  /** All available modes */
  allModes: ModeType[];
  /** Callback when collapse completes */
  onComplete?: () => void;
  /** Position offsets for each mode (from nucleus) */
  modePositions: Record<ModeType, { x: number; y: number }>;
  /** Colors for each mode */
  modeColors: Record<ModeType, string>;
  /** Icons for each mode (optional, for display during collapse) */
  modeIcons?: Record<ModeType, React.ReactNode>;
}

/**
 * Island state during collapse animation.
 */
interface CollapsingIsland {
  mode: ModeType;
  isTarget: boolean;
  scale: number;
  opacity: number;
}

/**
 * Sequential Collapse - Cell engulfing animation.
 *
 * When a mode is selected, the other 3 islands slide one-by-one
 * toward the selected island and merge via metaball effect.
 *
 * Animation sequence (200ms per collapse + 150ms delays):
 * 1. First non-selected island slides and merges (200ms)
 * 2. Second non-selected island slides and merges (200ms after first)
 * 3. Third non-selected island slides and merges (200ms after second)
 * 4. Nucleus pulse/absorption after each merge
 */
export function SequentialCollapse({
  selectedMode,
  allModes,
  onComplete,
  modePositions,
  modeColors,
  modeIcons,
}: SequentialCollapseProps) {
  const [isCollapsing, setIsCollapsing] = useState(false);
  const [collapsedCount, setCollapsedCount] = useState(0);

  // Start collapse when mode is selected
  useEffect(() => {
    if (selectedMode && !isCollapsing) {
      console.log('[SequentialCollapse] Starting collapse for mode:', selectedMode);
      setIsCollapsing(true);
      setCollapsedCount(0);
    }
  }, [selectedMode, isCollapsing]);

  // Track collapse progress
  useEffect(() => {
    if (isCollapsing && collapsedCount === 3) {
      // All islands collapsed
      console.log('[SequentialCollapse] Collapse complete');
      const timer = setTimeout(() => {
        onComplete?.();
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [isCollapsing, collapsedCount, onComplete]);

  // Get non-selected modes in collapse order
  const getNonSelectedModes = (): ModeType[] => {
    if (!selectedMode) return [];
    return allModes.filter(mode => mode !== selectedMode);
  };

  // Animate next collapse
  useEffect(() => {
    if (!isCollapsing || !selectedMode) return;

    const nonSelectedModes = getNonSelectedModes();
    if (collapsedCount < nonSelectedModes.length) {
      const timer = setTimeout(() => {
        console.log(`[SequentialCollapse] Collapsing island ${collapsedCount + 1}/3`);
        setCollapsedCount(prev => prev + 1);
      }, 200 + collapsedCount * 150); // 200ms collapse + 150ms delay

      return () => clearTimeout(timer);
    }
  }, [isCollapsing, collapsedCount, selectedMode, allModes]);

  // Calculate position for an island during collapse
  const getIslandPosition = (mode: ModeType, index: number) => {
    const nonSelectedModes = getNonSelectedModes();
    const modeIndexInNonSelected = nonSelectedModes.indexOf(mode);

    // If this mode hasn't started collapsing yet, stay at original position
    if (modeIndexInNonSelected >= collapsedCount) {
      return modePositions[mode];
    }

    // If this mode has collapsed, move toward selected mode position
    if (modeIndexInNonSelected < collapsedCount) {
      // Move closer to nucleus center as collapse progresses
      const progress = Math.min(1, collapsedCount - modeIndexInNonSelected);
      const targetX = 0; // Nucleus center
      const targetY = 0;
      const startX = modePositions[mode].x;
      const startY = modePositions[mode].y;

      return {
        x: startX + (targetX - startX) * progress,
        y: startY + (targetY - startY) * progress,
      };
    }

    return modePositions[mode];
  };

  if (!selectedMode || !isCollapsing) {
    return null;
  }

  const nonSelectedModes = getNonSelectedModes();

  return (
    <div className="absolute inset-0 pointer-events-none">
      <AnimatePresence>
        {nonSelectedModes.map((mode, index) => {
          const position = getIslandPosition(mode, index);
          const hasCollapsed = index < collapsedCount;
          const scale = hasCollapsed ? 0 : 1;
          const opacity = hasCollapsed ? 0 : 1;

          return (
            <motion.div
              key={mode}
              className="absolute left-1/2 top-1/2 rounded-full flex items-center justify-center"
              style={{
                width: '48px',
                height: '48px',
                backgroundColor: modeColors[mode],
                x: '-50%',
                y: '-50%',
                marginLeft: position.x,
                marginTop: position.y,
                scale,
                opacity,
              }}
              initial={{ scale: 1, opacity: 1 }}
              animate={{
                scale,
                opacity,
                marginLeft: position.x,
                marginTop: position.y,
              }}
              transition={{
                type: 'spring',
                stiffness: 400,
                damping: 20,
                duration: 0.2,
              }}
            >
              {/* Optional icon */}
              {modeIcons?.[mode]}
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
