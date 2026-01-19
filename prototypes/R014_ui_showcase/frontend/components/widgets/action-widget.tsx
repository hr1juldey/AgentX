"use client"

import { motion } from "framer-motion"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ActionWidgetProps {
  title?: string
  content?: string
  buttonText?: string
  variant?: "default" | "destructive" | "outline"
  onAction?: () => void
  onDismiss?: () => void
}

export function ActionWidget({ title, content, buttonText = "Click Me", variant = "default", onAction, onDismiss }: ActionWidgetProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.15 }}
      className="relative bg-card border border-border rounded-lg p-6 text-center"
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

      <Button onClick={onAction} variant={variant} className="w-full max-w-xs mx-auto">
        {buttonText}
      </Button>
    </motion.div>
  )
}
