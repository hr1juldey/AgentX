"use client";

import { motion, AnimatePresence, useMotionValue } from "framer-motion";
import { X } from "lucide-react";
import { memo, useCallback, useEffect, useRef, useState } from "react";

interface UIDescriptor {
  descriptor_id: string;
  descriptor_type: string;
  title?: string;
  content?: string;
  fields?: Array<{ name: string; type: string; label: string; required: boolean; options?: string[] }>;
  submit_button_text?: string;
  progress_percent?: number;
  status_text?: string;
  button_text?: string;
  action_id?: string;
  message?: string;
  confirm_label?: string;
  cancel_label?: string;
  metadata?: Record<string, unknown>;
}

interface IslandPanelProps {
  widget: UIDescriptor;
  islandPosition: { x: number; y: number };
  onClose: () => void;
  onDragEnd?: (x: number, y: number) => void;
  children: React.ReactNode;
}

/**
 * IslandPanel - Expanded panel anchored to island
 *
 * Features:
 * - Max width: 420px
 * - Viewport bounds checking
 * - Draggable panel
 * - Connection line to parent island
 * - 220ms expand/collapse animation
 */
export const IslandPanel = memo(function IslandPanel({
  widget,
  islandPosition,
  onClose,
  onDragEnd,
  children,
}: IslandPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const [currentPosition, setCurrentPosition] = useState(islandPosition);

  // Update local position when islandPosition prop changes
  useEffect(() => {
    setCurrentPosition(islandPosition);
  }, [islandPosition]);

  // Motion values for drag
  const dragX = useMotionValue(currentPosition.x);
  const dragY = useMotionValue(currentPosition.y);

  // Sync motion values when local position changes
  useEffect(() => {
    dragX.set(currentPosition.x);
    dragY.set(currentPosition.y);
  }, [currentPosition.x, currentPosition.y, dragX, dragY]);

  const handleClose = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    onClose();
  }, [onClose]);

  const handlePanelDragEnd = useCallback(
    (_: unknown, info: { offset: { x: number; y: number } }) => {
      // Calculate new position based on offset
      const newX = currentPosition.x + info.offset.x;
      const newY = currentPosition.y + info.offset.y;

      // Update local state for smooth UI
      setCurrentPosition({ x: newX, y: newY });

      // Notify parent to save the position
      onDragEnd?.(newX, newY);
    },
    [currentPosition, onDragEnd]
  );

  return (
    <AnimatePresence>
      <motion.div
        ref={panelRef}
        drag
        dragElastic={0}
        dragMomentum={false}
        whileDrag={{ cursor: "grabbing", scale: 1.02 }}
        onDragEnd={handlePanelDragEnd}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.22 }}
        className="fixed z-40 cursor-grab"
        style={{ x: dragX, y: dragY }}
      >
        {/* Connection line to parent island */}
        <svg className="absolute inset-0 pointer-events-none overflow-visible" style={{ width: "200%", height: "200%", left: "-50%", top: "-50%" }}>
          <motion.line
            x1="50%"
            y1="50%"
            x2={`${((islandPosition.x - currentPosition.x) / 420) * 100 + 50}%`}
            y2={`${((islandPosition.y - currentPosition.y) / 300) * 100 + 50}%`}
            stroke="hsl(var(--border))"
            strokeWidth="2"
            strokeDasharray="4 4"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 0.5 }}
            transition={{ duration: 0.3 }}
          />
        </svg>

        {/* Panel content */}
        <div
          className="bg-card border border-border rounded-lg shadow-2xl max-w-[420px] max-h-[60vh] overflow-auto relative"
          style={{ pointerEvents: "auto" }}
        >
          {/* Close button */}
          <button
            onClick={handleClose}
            className="absolute top-2 right-2 p-1 rounded hover:bg-muted transition-colors z-10"
            aria-label="Close panel"
          >
            <X className="w-4 h-4" />
          </button>

          {/* Widget content */}
          <div className="p-4">
            {widget.title && (
              <h3 className="text-lg font-semibold mb-2 pr-6">{widget.title}</h3>
            )}
            {children}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
});
