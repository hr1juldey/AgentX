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
}

export function CardWidget({ title, content, icon, actions, onDismiss }: CardWidgetProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="relative bg-card border border-border rounded-lg overflow-hidden"
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
        <div className="prose prose-sm dark:prose-invert max-w-none">
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
