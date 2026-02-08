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
 * @see openspec/changes/morphing-central-island/specs/mode-island-spawn
 */

'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MessageCircle, FileText, Camera } from 'lucide-react';
import { useState, useCallback, useEffect, useRef } from 'react';

export type ModeType = 'voice' | 'chat' | 'file' | 'camera';

export interface ModeIslandsProps {
  /** Whether longpress is active (show islands) */
  isLongpressActive: boolean;
  /** Callback when mode is selected - now includes current position */
  onModeSelect?: (mode: ModeType, currentPosition: { x: number; y: number }) => void;
  /** Color scheme from physics-cells (default: 'ai') */
  colorScheme?: 'raycast' | 'ai' | 'warm' | 'minimal' | 'custom';
  /** Whether collapse animation is active */
  isCollapsing?: boolean;
  /** Which mode was selected (for collapse animation) */
  selectedMode?: ModeType | null;
  /** Collapse progress (0-1 for Phase 1, 1-2 for Phase 2) */
  collapseProgress?: number;
  /** Whether collapse is complete (selected island moves to center) */
  collapseComplete?: boolean;
  /** Current positions of all islands (including drag offsets) */
  currentPositions?: Record<ModeType, { x: number; y: number }>;
  /** Whether islands should be shown (controlled by parent for reset) */
  shouldShowIslands?: boolean;
}

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
 */
export function ModeIslands({
  isLongpressActive,
  onModeSelect,
  colorScheme = 'ai',
  isCollapsing = false,
  selectedMode = null,
  collapseProgress = 0,
  collapseComplete = false,
  currentPositions = {},
  shouldShowIslands = true,
}: ModeIslandsProps) {
  const [hoveredMode, setHoveredMode] = useState<ModeType | null>(null);
  const [pressedMode, setPressedMode] = useState<ModeType | null>(null);

  // Drag state - persistent offsets for each mode
  const [draggingMode, setDraggingMode] = useState<ModeType | null>(null);
  const [dragOffsets, setDragOffsets] = useState<Record<ModeType, { x: number; y: number }>>({
    voice: { x: 0, y: 0 },
    chat: { x: 0, y: 0 },
    file: { x: 0, y: 0 },
    camera: { x: 0, y: 0 },
  });
  const dragStartRef = useRef({ x: 0, y: 0 });
  const dragStartOffsetRef = useRef({ x: 0, y: 0 }); // Store the offset when drag starts
  const [isDraggingActive, setIsDraggingActive] = useState(false);
  const didDragRef = useRef(false); // Track if drag actually occurred

  // Refs to track current prop values (to avoid stale closures)
  const isCollapsingRef = useRef(isCollapsing);
  const collapseCompleteRef = useRef(collapseComplete);

  // Keep refs in sync with props
  useEffect(() => {
    isCollapsingRef.current = isCollapsing;
  }, [isCollapsing]);

  useEffect(() => {
    collapseCompleteRef.current = collapseComplete;
  }, [collapseComplete]);

  // Handle drag start
  const handleDragStart = useCallback((e: React.MouseEvent | React.TouchEvent, mode: ModeType) => {
    // Check refs instead of closure values to get fresh state
    if (isCollapsingRef.current || collapseCompleteRef.current) return;

    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;

    dragStartRef.current = { x: clientX, y: clientY };
    dragStartOffsetRef.current = dragOffsets[mode]; // Remember current offset
    didDragRef.current = false; // Reset drag flag
    setDraggingMode(mode);
    setIsDraggingActive(false);
    setPressedMode(mode);
  }, [isCollapsing, collapseComplete, dragOffsets]);

  // Handle document-level drag move
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!draggingMode || (isCollapsing || collapseComplete)) return;

      const dx = e.clientX - dragStartRef.current.x;
      const dy = e.clientY - dragStartRef.current.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance > 5) { // Drag threshold
        didDragRef.current = true; // Mark as drag occurred
        setIsDraggingActive(true);

        // Update offset: starting offset + current drag delta
        setDragOffsets(prev => ({
          ...prev,
          [draggingMode]: {
            x: dragStartOffsetRef.current.x + dx,
            y: dragStartOffsetRef.current.y + dy,
          },
        }));
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (!draggingMode || (isCollapsing || collapseComplete)) return;

      const touch = e.touches[0];
      const dx = touch.clientX - dragStartRef.current.x;
      const dy = touch.clientY - dragStartRef.current.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance > 5) {
        didDragRef.current = true;
        setIsDraggingActive(true);

        setDragOffsets(prev => ({
          ...prev,
          [draggingMode]: {
            x: dragStartOffsetRef.current.x + dx,
            y: dragStartOffsetRef.current.y + dy,
          },
        }));
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
  }, [draggingMode, isCollapsing, collapseComplete]);

  // Handle drag end
  const handleDragEnd = useCallback(() => {
    if (draggingMode) {
      const wasDragging = didDragRef.current;
      console.log(`[ModeIslands] Drag ended: ${draggingMode}, wasDragging: ${wasDragging}, final offset:`, dragOffsets[draggingMode]);
      setDraggingMode(null);
      setIsDraggingActive(false);
      setPressedMode(null);
      // Don't reset didDragRef here - let the click handler check it
      // Don't reset dragOffsets - keep the position where dropped
    }
  }, [draggingMode, dragOffsets]);

  // Handle click - only fire if not dragging, pass current position
  const handleClick = useCallback((mode: ModeType) => {
    // Use refs to get fresh prop values instead of stale closure values
    if (!didDragRef.current && !isCollapsingRef.current && !collapseCompleteRef.current) {
      // Calculate current position (original + drag offset)
      const currentPos = {
        x: MODES[mode].position.x + dragOffsets[mode].x,
        y: MODES[mode].position.y + dragOffsets[mode].y,
      };
      console.log(`[ModeIslands] Click detected (not drag): ${mode} at current position:`, currentPos);
      console.log(`[ModeIslands] State check - isCollapsing: ${isCollapsingRef.current}, collapseComplete: ${collapseCompleteRef.current}`);
      onModeSelect?.(mode, currentPos);
    } else {
      console.log(`[ModeIslands] Click ignored - was drag: ${mode}, didDrag: ${didDragRef.current}, isCollapsing: ${isCollapsingRef.current}, collapseComplete: ${collapseCompleteRef.current}`);
    }
  }, [onModeSelect, dragOffsets]); // Remove isCollapsing and collapseComplete from deps

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
            const storedOffset = dragOffsets[mode as ModeType]; // Get stored offset for this mode

            // HIDE non-selected islands after collapse completes
            // Only the selected island should remain visible
            // Also hide all islands if no mode is selected but collapseComplete is true (reset state)
            if (collapseComplete && !isSelected) {
              return null;
            }

            // Also hide islands if we're in collapsed state but no mode selected (shouldn't happen but safety check)
            if (collapseComplete && !selectedMode) {
              return null;
            }

            // Calculate position during collapse
            let currentX = config.position.x + storedOffset.x; // Apply stored offset
            let currentY = config.position.y + storedOffset.y;
            let currentScale = 1;
            let currentOpacity = 1;
            let currentZIndex = 10;

            // Apply additional drag offset while actively dragging (visual feedback only)
            if (isDraggingThis) {
              currentZIndex = 50;
              currentScale = 1.05;
            }

            // During collapse, non-selected islands animate toward SELECTED island's CURRENT position
            if (isCollapsing && selectedMode && !isSelected) {
              // Get selected mode's CURRENT position (original + drag offset)
              const selectedOffset = dragOffsets[selectedMode] || { x: 0, y: 0 };
              const selectedOriginalPos = MODES[selectedMode].position;
              const targetPos = {
                x: selectedOriginalPos.x + selectedOffset.x,
                y: selectedOriginalPos.y + selectedOffset.y,
              };
              const progress = Math.min(1, collapseProgress * 1.5); // Speed up collapse

              // Animate from THIS island's current position toward selected island's current position
              const thisCurrentX = config.position.x + storedOffset.x;
              const thisCurrentY = config.position.y + storedOffset.y;

              currentX = thisCurrentX + (targetPos.x - thisCurrentX) * progress;
              currentY = thisCurrentY + (targetPos.y - thisCurrentY) * progress;

              // Scale down as it approaches selected island
              if (progress > 0.8) {
                currentScale = 1 - ((progress - 0.8) / 0.2); // Scale 1 → 0 at 80%+ progress
                currentOpacity = currentScale;
              }

              console.log(`[ModeIslands] ${mode}: collapsing toward ${selectedMode} (current pos: ${targetPos.x.toFixed(0)}, ${targetPos.y.toFixed(0)}), progress=${progress.toFixed(2)}, my pos=(${currentX.toFixed(0)}, ${currentY.toFixed(0)})`);
            }

            // After collapse complete, selected island moves from ITS CURRENT position to center
            if (collapseComplete && isSelected) {
              // Animate from THIS island's CURRENT position (where user dragged it) to center (0, 0)
              const thisCurrentX = config.position.x + storedOffset.x;
              const thisCurrentY = config.position.y + storedOffset.y;
              const centerMoveProgress = Math.min(1, (collapseProgress - 1) * 2); // Speed up final move

              currentX = thisCurrentX + (0 - thisCurrentX) * centerMoveProgress;
              currentY = thisCurrentY + (0 - thisCurrentY) * centerMoveProgress;
              currentZIndex = 50; // Selected island on top during final move

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
                className="absolute left-1/2 top-1/2 pointer-events-auto flex items-center justify-center rounded-full"
                style={{
                  width: '48px',
                  height: '48px',
                  backgroundColor: `var(${config.colorVar}, ${config.fallbackColor})`,
                  // Position based on collapse state
                  x: '-50%',
                  y: '-50%',
                  marginLeft: currentX,
                  marginTop: currentY,
                  boxShadow: isDraggingThis ? '0 10px 30px rgba(0, 0, 0, 0.3)' : '0 2px 8px rgba(0, 0, 0, 0.2)',
                  border: 'none',
                  outline: 'none',
                  cursor: (isCollapsing || collapseComplete) ? 'default' : (isDraggingThis ? 'grabbing' : 'grab'),
                  opacity: currentOpacity,
                  zIndex: isDraggingThis ? 50 : currentZIndex,
                }}
                // Emergence animation with stagger
                initial={{ scale: 0, opacity: 0 }}
                animate={{
                  scale: isDraggingThis ? 1.05 : (isPressed ? 0.95 : isHovered ? 1.05 : currentScale),
                  opacity: currentOpacity,
                }}
                exit={{
                  scale: 0,
                  opacity: 0,
                  transition: {
                    duration: 0.15,
                  },
                }}
                transition={{
                  type: 'spring',
                  stiffness: 200,
                  damping: 25,
                  delay: index * 0.05, // Stagger: 50ms between each
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
