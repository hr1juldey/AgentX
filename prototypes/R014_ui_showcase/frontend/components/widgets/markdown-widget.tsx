"use client"

import { motion } from "framer-motion"
import { X } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface MarkdownWidgetProps {
  content: string
  onDismiss?: () => void
}

export function MarkdownWidget({ content, onDismiss }: MarkdownWidgetProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      className="relative bg-card border border-border rounded-lg p-6"
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
      <div className="prose prose-sm dark:prose-invert max-w-none">
        <ReactMarkdown remark={remarkGfm}>{content}</ReactMarkdown>
      </div>
    </motion.div>
  )
}
