"use client"

import { motion, AnimatePresence } from "framer-motion"
import { X, Layers, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { LucideIcon } from "@/components/ui/icon"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { memo, useCallback } from "react"

interface CardWidgetProps {
  title?: string
  content: string
  icon?: string
  actions?: Array<{ label: string; action: string; variant?: string }>
  collapsed?: boolean
  onToggleCollapse?: () => void
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
  disableDrag?: boolean // When true, widget is not draggable (for embedded use in IsolatedWidget)
}

export const CardWidget = memo(function CardWidget({
  title,
  content,
  icon,
  actions,
  collapsed = false,
  onToggleCollapse,
  onDismiss,
  dragPosition,
  onDragEnd,
  disableDrag = false
}: CardWidgetProps) {
  const handleDragEnd = useCallback((_: any, info: any) => {
    onDragEnd?.(
      (dragPosition?.x || 0) + info.offset.x,
      (dragPosition?.y || 0) + info.offset.y
    );
  }, [onDragEnd, dragPosition]);

  const handleDismiss = useCallback(() => {
    onDismiss?.();
  }, [onDismiss]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      drag={disableDrag ? false : undefined}
      dragElastic={0.1}
      dragMomentum={false}
      dragConstraints={false}
      whileDrag={disableDrag ? undefined : { scale: 1.02, cursor: "grabbing", zIndex: 9999 }}
      onDragEnd={disableDrag ? undefined : handleDragEnd}
      style={{ x: dragPosition?.x || 0, y: dragPosition?.y || 0 }}
      className={`relative bg-card border border-border rounded-lg overflow-hidden shadow-lg hover:shadow-xl ${disableDrag ? '' : 'cursor-grab'}`}
    >
      {/* Widget Header - Click to toggle (Jira-style) */}
      <div
        className="flex items-center justify-between px-4 py-2 border-b bg-muted/30 cursor-pointer hover:bg-muted/50"
        onClick={() => onToggleCollapse?.()}
      >
        <div className="flex items-center gap-2">
          {icon ? (
            <LucideIcon name={icon} className="w-4 h-4 text-primary" />
          ) : (
            <Layers className="w-4 h-4 text-primary" />
          )}
          <span className="text-sm font-medium">{title || "Card"}</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Chevron indicator - rotates based on collapsed state */}
          <motion.div
            animate={{ rotate: collapsed ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          </motion.div>

          {/* Dismiss button - stopPropagation to prevent collapse */}
          {onDismiss && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDismiss();
              }}
              className="p-1 rounded hover:bg-destructive/10 hover:text-destructive transition-colors"
              aria-label="Dismiss"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Card Content - Collapsible with smart animation */}
      <AnimatePresence initial={false} mode="wait">
        {!collapsed && (
          <motion.div
            layout="position"
            initial={{ height: 0, opacity: 0, scaleY: 0.95 }}
            animate={{ height: "auto", opacity: 1, scaleY: 1 }}
            exit={{ height: 0, opacity: 0, scaleY: 0.95 }}
            transition={{
              height: { type: "spring", stiffness: 400, damping: 30 },
              opacity: { duration: 0.15 },
              scaleY: { type: "spring", stiffness: 400, damping: 30 }
            }}
            style={{ originY: 0 }}
            className="overflow-hidden"
          >
            <div className="p-6">
              <div className="text-sm leading-relaxed prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
              </div>
              {actions && actions.length > 0 && (
                <div className="flex gap-2 mt-4">
                  {actions.map((action, i) => (
                    <Button
                      key={i}
                      variant={action.variant as any || "outline"}
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        console.log("Action:", action.action);
                      }}
                    >
                      {action.label}
                    </Button>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});
