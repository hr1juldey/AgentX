"use client"

import { motion } from "framer-motion"
import { X } from "lucide-react"

interface ProgressWidgetProps {
  title?: string
  content?: string
  value?: number
  indeterminate?: boolean
  statusText?: string
  onDismiss?: () => void
}

export function ProgressWidget({ title, content, value = 0, indeterminate = false, statusText, onDismiss }: ProgressWidgetProps) {
  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.2 }}
      className="relative bg-card border border-border rounded-lg p-6 overflow-hidden"
    >
      {onDismiss && (
        <button
          onClick={onDismiss}
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
}
