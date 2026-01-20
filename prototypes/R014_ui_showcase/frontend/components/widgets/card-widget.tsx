"use client"

import { motion } from "framer-motion"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { LucideIcon } from "@/components/ui/icon"

interface CardWidgetProps {
  title?: string
  content: string
  icon?: string
  actions?: Array<{ label: string; action: string; variant?: string }>
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
}

export function CardWidget({ title, content, icon, actions, onDismiss, dragPosition, onDragEnd }: CardWidgetProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
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
      className="relative bg-card border border-border rounded-lg overflow-hidden cursor-grab shadow-lg hover:shadow-xl"
    >
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="absolute top-2 right-2 p-1 rounded hover:bg-muted transition-colors z-10"
          aria-label="Dismiss"
        >
          <X className="w-4 h-4" />
        </button>
      )}
      <div className="p-6">
        {title && (
          <div className="flex items-center gap-2 mb-3">
            {icon && <LucideIcon name={icon} className="w-5 h-5 text-primary" />}
            <h3 className="text-lg font-semibold">{title}</h3>
          </div>
        )}
        <div className="text-sm leading-relaxed">
          <p>{content}</p>
        </div>
        {actions && actions.length > 0 && (
          <div className="flex gap-2 mt-4">
            {actions.map((action, i) => (
              <Button
                key={i}
                variant={action.variant as any || "outline"}
                size="sm"
                onClick={() => console.log("Action:", action.action)}
              >
                {action.label}
              </Button>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  )
}
