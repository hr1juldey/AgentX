"use client"

import { motion } from "framer-motion"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ConfirmationWidgetProps {
  title?: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: "default" | "destructive"
  onConfirm?: () => void
  onCancel?: () => void
  onDismiss?: () => void
}

export function ConfirmationWidget({
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  variant = "default",
  onConfirm,
  onCancel,
  onDismiss,
}: ConfirmationWidgetProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.2 }}
      className="relative bg-card border border-border rounded-lg p-6 max-w-md"
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
      {title && (
        <h3 className="text-lg font-semibold mb-2">
          {variant === "destructive" && <span className="text-destructive">⚠️ </span>}
          {title}
        </h3>
      )}
      <p className="text-sm mb-6">{message}</p>

      <div className="flex gap-3 justify-end">
        <Button variant="outline" onClick={onCancel}>
          {cancelLabel}
        </Button>
        <Button variant={variant} onClick={onConfirm}>
          {confirmLabel}
        </Button>
      </div>
    </motion.div>
  )
}
