/**
 * Mode Islands component for Morphing Central Island.
 *
 * Four circular mode islands that emerge from nucleus during longpress.
 * Each represents an interaction mode: Voice, Chat, File, Camera.
 *
 * Uses physics-cells color scheme variables for consistency.
 * Emerges with spring physics like biological cell division.
 * Draggable with spring physics during idle state.
 *
 * Uses Zustand store for state management to avoid stale closure issues.
 *
 * @see openspec/changes/morphing-central-island/specs/mode-island-spawn
 */

'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MessageCircle, FileText, Camera } from 'lucide-react';
import { useState, useCallback, useEffect, useRef } from 'react';
import { useMorphingIslandStore, type ModeType } from './store';

export type ColorSchemeType = 'raycast' | 'ai' | 'warm' | 'minimal' | 'custom';

export interface ModeIslandsProps {
  /** Whether longpress is active (show islands) */
  isLongpressActive: boolean;
  /** Callback when mode is selected - now includes current position */
  onModeSelect?: (mode: ModeType, currentPosition: { x: number; y: number }) => void;
  /** Color scheme from physics-cells (default: 'ai') */
  colorScheme?: ColorSchemeType;
  /** Collapse progress (0-1 for Phase 1, 1-2 for Phase 2) */
  collapseProgress?: number;
  /** Whether islands should be shown (controlled by parent for reset) */
  shouldShowIslands?: boolean;
}

// Re-export ModeType for convenience
export type { ModeType };

/**
 * Mode configuration with colors and positions.
 */
const MODES = {
  voice: {
    icon: Mic,
    colorVar: '--scheme-cell-3',
    fallbackColor: '#A78BFA',
    position: { x: 0, y: -80 }, // Top
    label: 'Voice',
  },
  chat: {
    icon: MessageCircle,
    colorVar: '--scheme-cell-2',
    fallbackColor: '#6366F1',
    position: { x: -80, y: 0 }, // Left
    label: 'Chat',
  },
  file: {
    icon: FileText,
    colorVar: '--scheme-cell-1',
    fallbackColor: '#22D3EE',
    position: { x: 80, y: 0 }, // Right
    label: 'File',
  },
  camera: {
    icon: Camera,
    colorVar: '--scheme-cell-5',
    fallbackColor: '#EC4899',
    position: { x: 0, y: 80 }, // Bottom
    label: 'Camera',
  },
} as const;

/**
 * Mode Islands - Spawns from nucleus on longpress.
 *
 * Features organic spring emergence, cardinal positioning,
 * physics-cells color scheme integration, and draggable behavior.
 *
 * Collapse behavior: All non-selected islands slide toward and merge
 * into the SELECTED island (not nucleus center). After merge completes,
 * selected island moves to center position.
 *
 * Uses Zustand store for state management to avoid stale closure issues.
 */
export function ModeIslands({
  isLongpressActive,
  onModeSelect,
  colorScheme = 'ai',
  collapseProgress = 0,
  shouldShowIslands = true,
}: ModeIslandsProps) {
  // Local UI state only
  const [hoveredMode, setHoveredMode] = useState<ModeType | null>(null);
  const [pressedMode, setPressedMode] = useState<ModeType | null>(null);

  // Store state - drag offsets, collapse state, selected mode
  const dragOffsets = useMorphingIslandStore((state) => state.dragOffsets);
  const selectedMode = useMorphingIslandStore((state) => state.selectedMode);
  const isCollapsing = useMorphingIslandStore((state) => state.isCollapsing);
  const collapseComplete = useMorphingIslandStore((state) => state.collapseComplete);
  const collapseIslands = useMorphingIslandStore((state) => state.collapseIslands);
  const collapseIslandsCount = useMorphingIslandStore((state) => state.collapseIslandsCount);

  // Store actions
  const setDragOffset = useMorphingIslandStore((state) => state.setDragOffset);
  const setSelectedMode = useMorphingIslandStore((state) => state.setSelectedMode);
  const getSelectedModeCurrentPosition = useMorphingIslandStore((state) => state.getSelectedModeCurrentPosition);
  const getCollapseIsland = useMorphingIslandStore((state) => state.getCollapseIsland);

  // Local drag state (not in store as it's only for active drag)
  const [draggingMode, setDraggingMode] = useState<ModeType | null>(null);
  const [isDraggingActive, setIsDraggingActive] = useState(false);
  const dragStartRef = useRef({ x: 0, y: 0 });
  const dragStartOffsetRef = useRef({ x: 0, y: 0 });
  const didDragRef = useRef(false);

  // Handle drag start
  const handleDragStart = useCallback((e: React.MouseEvent | React.TouchEvent, mode: ModeType) => {
    // Get fresh state from store to avoid stale closures
    const storeState = useMorphingIslandStore.getState();
    if (storeState.isCollapsing || storeState.collapseComplete) return;

    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;

    dragStartRef.current = { x: clientX, y: clientY };
    dragStartOffsetRef.current = storeState.dragOffsets[mode];
    didDragRef.current = false;
    setDraggingMode(mode);
    setIsDraggingActive(false);
    setPressedMode(mode);
  }, []);

  // Handle document-level drag move
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!draggingMode) return;

      // Check fresh state from store
      const storeState = useMorphingIslandStore.getState();
      if (storeState.isCollapsing || storeState.collapseComplete) return;

      const dx = e.clientX - dragStartRef.current.x;
      const dy = e.clientY - dragStartRef.current.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance > 5) {
        didDragRef.current = true;
        setIsDraggingActive(true);

        // Update offset in store
        const newOffset = {
          x: dragStartOffsetRef.current.x + dx,
          y: dragStartOffsetRef.current.y + dy,
        };
        setDragOffset(draggingMode, newOffset);
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (!draggingMode) return;

      const storeState = useMorphingIslandStore.getState();
      if (storeState.isCollapsing || storeState.collapseComplete) return;

      const touch = e.touches[0];
      const dx = touch.clientX - dragStartRef.current.x;
      const dy = touch.clientY - dragStartRef.current.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance > 5) {
        didDragRef.current = true;
        setIsDraggingActive(true);

        const newOffset = {
          x: dragStartOffsetRef.current.x + dx,
          y: dragStartOffsetRef.current.y + dy,
        };
        setDragOffset(draggingMode, newOffset);
      }
    };

    if (draggingMode) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('touchmove', handleTouchMove, { passive: true });
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('touchmove', handleTouchMove);
    };
  }, [draggingMode, setDragOffset]);

  // Handle drag end
  const handleDragEnd = useCallback(() => {
    if (draggingMode) {
      const wasDragging = didDragRef.current;
      const currentOffset = useMorphingIslandStore.getState().dragOffsets[draggingMode];
      console.log(`[ModeIslands] Drag ended: ${draggingMode}, wasDragging: ${wasDragging}, final offset:`, currentOffset);
      setDraggingMode(null);
      setIsDraggingActive(false);
      setPressedMode(null);
    }
  }, [draggingMode]);

  // Handle click - only fire if not dragging, pass current position
  const handleClick = useCallback((mode: ModeType) => {
    if (didDragRef.current) {
      console.log(`[ModeIslands] Click ignored - was drag: ${mode}`);
      return;
    }

    // Get fresh state from store
    const storeState = useMorphingIslandStore.getState();
    if (storeState.isCollapsing || storeState.collapseComplete) {
      console.log(`[ModeIslands] Click ignored - collapsing: ${mode}`);
      return;
    }

    // Calculate current position using store's getter (synchronous, no stale closures)
    const currentPos = useMorphingIslandStore.getState().getCurrentPosition(mode);
    console.log(`[ModeIslands] Click detected (not drag): ${mode} at current position:`, currentPos);
    onModeSelect?.(mode, currentPos);
  }, [onModeSelect]);

  return (
    <AnimatePresence>
      {isLongpressActive && shouldShowIslands && (
        <div className="absolute inset-0 pointer-events-none">
          {Object.entries(MODES).map(([mode, config], index) => {
            const Icon = config.icon;
            const isHovered = hoveredMode === mode;
            const isPressed = pressedMode === mode;
            const isSelected = mode === selectedMode;
            const isDraggingThis = draggingMode === mode && isDraggingActive;
            const storedOffset = dragOffsets[mode as ModeType];

            // HIDE non-selected islands after collapse completes
            if (collapseComplete && !isSelected) {
              return null;
            }

            // Also hide islands if we're in collapsed state but no mode selected
            if (collapseComplete && !selectedMode) {
              return null;
            }

            // Calculate position during collapse
            let currentX = config.position.x + storedOffset.x;
            let currentY = config.position.y + storedOffset.y;
            let currentScale = 1;
            let currentOpacity = 1;
            let currentZIndex = 10;

            // Apply additional drag offset while actively dragging (visual feedback only)
            if (isDraggingThis) {
              currentZIndex = 50;
              currentScale = 1.05;
            }

            // During collapse, non-selected islands animate TOWARD SELECTED island's CURRENT position
            // SEQUENTIAL COLLAPSE: Each island waits its turn based on distance (closest first)
            if (isCollapsing && selectedMode && !isSelected) {
              const targetPos = getSelectedModeCurrentPosition();
              const collapseInfo = getCollapseIsland(mode as ModeType);

              if (targetPos && collapseInfo) {
                const { order, distance } = collapseInfo;
                const totalIslands = collapseIslandsCount;

                // Sequential collapse: each island gets a slice of the collapse progress
                // Phase 1 is divided into equal parts for each island
                // Example: 3 islands, each gets 1/3 of progress = 0.33 each
                const progressPerIsland = 1 / totalIslands;

                // Calculate this island's start and end progress within Phase 1
                const startProgress = order * progressPerIsland;
                const endProgress = startProgress + progressPerIsland;

                // Map overall collapseProgress to this island's local progress
                // Overall progress 0-1 maps to Phase 1, so we use collapseProgress directly
                const overallProgress = Math.min(1, collapseProgress * 1.5);
                let localProgress = 0;

                // Island waits for its turn, then animates
                if (overallProgress >= startProgress) {
                  // This island's turn has started
                  localProgress = Math.min(1, (overallProgress - startProgress) / progressPerIsland);
                } else {
                  // This island hasn't started collapsing yet - stay at original position
                  localProgress = 0;
                }

                // Animate from THIS island's current position toward selected island's current position
                const thisCurrentX = config.position.x + storedOffset.x;
                const thisCurrentY = config.position.y + storedOffset.y;

                currentX = thisCurrentX + (targetPos.x - thisCurrentX) * localProgress;
                currentY = thisCurrentY + (targetPos.y - thisCurrentY) * localProgress;

                // Scale down as it approaches selected island (during animation)
                if (localProgress > 0) {
                  // Start scaling once animation begins
                  const scaleProgress = Math.max(0, localProgress - 0.7) / 0.3; // Scale only in last 30%
                  currentScale = 1 - scaleProgress;
                  currentOpacity = 1 - scaleProgress;
                }

                // Keep island visible but small after collapse (don't hide completely)
                // This allows Phase 2 to show the merged state before selected island moves to center
                if (localProgress >= 1) {
                  // Island has reached target - stay small but visible at merged position
                  currentScale = 0.3;
                  currentOpacity = 0.8;
                }

                console.log(`[ModeIslands] ${mode}: order=${order}/${totalIslands - 1}, dist=${distance.toFixed(0)}px, overall=${overallProgress.toFixed(2)}, local=${localProgress.toFixed(2)}, my pos=(${currentX.toFixed(0)}, ${currentY.toFixed(0)})`);
              }
            }

            // After collapse complete, selected island moves from ITS CURRENT position to center
            if (collapseComplete && isSelected) {
              // Animate from THIS island's CURRENT position (where user dragged it) to center (0, 0)
              const thisCurrentX = config.position.x + storedOffset.x;
              const thisCurrentY = config.position.y + storedOffset.y;
              const centerMoveProgress = Math.min(1, (collapseProgress - 1) * 2);

              currentX = thisCurrentX + (0 - thisCurrentX) * centerMoveProgress;
              currentY = thisCurrentY + (0 - thisCurrentY) * centerMoveProgress;
              currentZIndex = 50;

              console.log(`[ModeIslands] ${mode}: moving to center from (${thisCurrentX.toFixed(0)}, ${thisCurrentY.toFixed(0)}), progress=${centerMoveProgress.toFixed(2)}, pos=(${currentX.toFixed(0)}, ${currentY.toFixed(0)})`);
            }

            return (
              <motion.button
                key={mode}
                data-mode={mode}
                data-color-scheme={colorScheme}
                onClick={() => handleClick(mode as ModeType)}
                onMouseEnter={() => !isCollapsing && !collapseComplete && !isDraggingActive && setHoveredMode(mode as ModeType)}
                onMouseLeave={() => setHoveredMode(null)}
                onMouseDown={(e) => handleDragStart(e, mode as ModeType)}
                onMouseUp={handleDragEnd}
                onTouchStart={(e) => handleDragStart(e, mode as ModeType)}
                onTouchEnd={handleDragEnd}
                className="pointer-events-auto flex items-center justify-center rounded-full"
                style={{
                  width: '48px',
                  height: '48px',
                  backgroundColor: `var(${config.colorVar}, ${config.fallbackColor})`,
                  boxShadow: isDraggingThis ? '0 10px 30px rgba(0, 0, 0, 0.3)' : '0 2px 8px rgba(0, 0, 0, 0.2)',
                  border: 'none',
                  outline: 'none',
                  cursor: (isCollapsing || collapseComplete) ? 'default' : (isDraggingThis ? 'grabbing' : 'grab'),
                  zIndex: isDraggingThis ? 50 : currentZIndex,
                }}
                // Animate position, scale, and opacity with Framer Motion for smooth transitions
                initial={{ scale: 0, opacity: 0, x: 0, y: 0 }}
                animate={{
                  x: currentX,
                  y: currentY,
                  scale: isDraggingThis ? 1.05 : (isPressed ? 0.95 : isHovered ? 1.05 : currentScale),
                  opacity: currentOpacity,
                }}
                exit={{
                  scale: 0,
                  opacity: 0,
                  x: 0,
                  y: 0,
                  transition: {
                    duration: 0.15,
                  },
                }}
                transition={{
                  type: 'spring',
                  stiffness: 200,
                  damping: 25,
                  delay: index * 0.05, // Stagger: 50ms between each
                  // Smooth position transitions during collapse
                  x: { type: 'spring', stiffness: 150, damping: 20 },
                  y: { type: 'spring', stiffness: 150, damping: 20 },
                }}
              >
                {/* Mode icon */}
                <Icon
                  size={24}
                  style={{ color: 'white' }}
                  strokeWidth={2}
                />
              </motion.button>
            );
          })}
        </div>
      )}
    </AnimatePresence>
  );
}
