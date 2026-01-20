"use client";

import { motion, AnimatePresence } from "framer-motion";
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
  pushVector?: { x: number; y: number };
  onClose: () => void;
  children: React.ReactNode;
}

/**
 * IslandPanel - Expanded panel anchored to island with collision support
 *
 * Features:
 * - Max width: 420px
 * - Viewport bounds checking
 * - Connection line to parent island
 * - Accepts push vector from collision resolver
 * - 220ms expand/collapse animation
 */
export const IslandPanel = memo(function IslandPanel({
  widget,
  islandPosition,
  pushVector,
  onClose,
  children,
}: IslandPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const [adjustedPosition, setAdjustedPosition] = useState(islandPosition);

  // Apply push vector and adjust for viewport bounds
  useEffect(() => {
    if (typeof window === "undefined") return;

    const panel = panelRef.current;
    if (!panel) return;

    const panelWidth = 420;
    const panelHeight = panel.offsetHeight || 300;

    // Calculate position with push vector
    let x = islandPosition.x + (pushVector?.x || 0);
    let y = islandPosition.y + (pushVector?.y || 0);

    // Get viewport dimensions
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // Calculate panel bounds (assuming panel is centered on position)
    const panelLeft = x - panelWidth / 2;
    const panelRight = x + panelWidth / 2;
    const panelTop = y - panelHeight / 2;
    const panelBottom = y + panelHeight / 2;

    // Adjust for viewport bounds
    if (panelLeft < 16) {
      x = 16 + panelWidth / 2;
    } else if (panelRight > viewportWidth - 16) {
      x = viewportWidth - 16 - panelWidth / 2;
    }

    if (panelTop < 16) {
      y = 16 + panelHeight / 2;
    } else if (panelBottom > viewportHeight - 16) {
      y = viewportHeight - 16 - panelHeight / 2;
    }

    setAdjustedPosition({ x, y });
  }, [islandPosition, pushVector]);

  const handleClose = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    onClose();
  }, [onClose]);

  return (
    <AnimatePresence>
      <motion.div
        ref={panelRef}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.22 }}
        className="fixed z-40"
        style={{
          left: adjustedPosition.x,
          top: adjustedPosition.y,
          transform: "translate(-50%, -50%)",
        }}
      >
        {/* Connection line to parent island */}
        <svg className="absolute inset-0 pointer-events-none overflow-visible" style={{ width: "200%", height: "200%", left: "-50%", top: "-50%" }}>
          <motion.line
            x1="50%"
            y1="50%"
            x2={`${((islandPosition.x - adjustedPosition.x) / 420) * 100 + 50}%`}
            y2={`${((islandPosition.y - adjustedPosition.y) / 300) * 100 + 50}%`}
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
