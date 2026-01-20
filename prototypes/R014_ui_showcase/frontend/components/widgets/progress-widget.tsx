"use client"
import { memo, useCallback } from "react"

import { motion } from "framer-motion"
import { X } from "lucide-react"

interface ProgressWidgetProps {
  title?: string
  content?: string
  value?: number
  indeterminate?: boolean
  statusText?: string
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
}

export const ProgressWidget = memo(function ProgressWidget({
  title,
  content,
  value = 0,
  indeterminate = false,
  statusText,
  onDismiss,
  dragPosition,
  onDragEnd
}: ProgressWidgetProps) {
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
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.2 }}
      drag
      dragElastic={0.2}
      dragMomentum={false}
      dragConstraints={{ left: -500, right: 500, top: -500, bottom: 500 }}
      whileDrag={{ scale: 1.02, rotate: 1, cursor: "grabbing", zIndex: 50 }}
      onDragEnd={(_, info) => onDragEnd?.(
        (dragPosition?.x || 0) + info.offset.x,
        (dragPosition?.y || 0) + info.offset.y
      )}
      style={{ x: dragPosition?.x || 0, y: dragPosition?.y || 0 }}
      className="relative bg-card cursor-grab shadow-lg hover:shadow-xl border border-border rounded-lg p-6 overflow-hidden"
    >
      {onDismiss && (
        <button
          onClick={handleDismiss}
          className="absolute top-2 right-2 p-1 rounded hover:bg-muted transition-colors"
          aria-label="Dismiss"
        >
          <X className="w-4 h-4" />
        </button>
      )}
      {title && <h3 className="text-lg font-semibold mb-2">{title}</h3>}
      {content && <p className="text-sm text-muted-foreground mb-4">{content}</p>}

      <div className="space-y-2">
        <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: indeterminate ? "100%" : `${value * 100}%` }}
            transition={{ duration: indeterminate ? 1 : 0.5 }}
            className={`h-full bg-primary ${indeterminate ? "animate-pulse" : ""}`}
          />
        </div>
        {statusText && (
          <p className="text-sm text-muted-foreground">{statusText}</p>
        )}
      </div>
    </motion.div>
  )
});
