"use client"

import { motion, AnimatePresence } from "framer-motion"
import { X, FileText, ChevronDown } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { memo, useCallback, useMemo } from "react"

// Strip markdown code block wrapper if present
function stripMarkdownWrapper(content: string): string {
  let cleaned = content

  // Remove ```markdown or ``` at the start
  if (cleaned.startsWith("```markdown")) {
    cleaned = cleaned.slice(11) // Remove "```markdown"
  } else if (cleaned.startsWith("```")) {
    cleaned = cleaned.slice(3) // Remove "```"
  }

  // Remove leading newline after the opening marker
  cleaned = cleaned.trimStart()

  // Remove ``` at the end
  if (cleaned.endsWith("```")) {
    cleaned = cleaned.slice(0, -3)
  }

  // Remove trailing whitespace
  cleaned = cleaned.trimEnd()

  return cleaned
}

interface MarkdownWidgetProps {
  content: string
  title?: string
  collapsed?: boolean
  onToggleCollapse?: () => void
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
}

export const MarkdownWidget = memo(function MarkdownWidget({
  content,
  title = "Markdown",
  collapsed = false,
  onToggleCollapse,
  onDismiss,
  dragPosition,
  onDragEnd
}: MarkdownWidgetProps) {
  // Strip markdown code block wrapper if present (memoized to prevent re-renders)
  const cleanedContent = useMemo(() => stripMarkdownWrapper(content), [content]);

  // Stable drag handler to prevent re-renders
  const handleDragEnd = useCallback((_: any, info: any) => {
    onDragEnd?.(
      (dragPosition?.x || 0) + info.offset.x,
      (dragPosition?.y || 0) + info.offset.y
    );
  }, [onDragEnd, dragPosition]);

  // Stable dismiss handler
  const handleDismiss = useCallback(() => {
    onDismiss?.();
  }, [onDismiss]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      drag
      dragElastic={0.1}
      dragMomentum={false}
      dragConstraints={false}
      whileDrag={{ scale: 1.02, cursor: "grabbing", zIndex: 9999 }}
      onDragEnd={handleDragEnd}
      style={{ x: dragPosition?.x || 0, y: dragPosition?.y || 0 }}
      className="relative bg-card border border-border rounded-lg cursor-grab shadow-lg hover:shadow-xl max-w-[480px]"
    >
      {/* Widget Header - Click to toggle (Jira-style) */}
      <div
        className="flex items-center justify-between px-4 py-2 border-b bg-muted/30 cursor-pointer hover:bg-muted/50"
        onClick={() => onToggleCollapse?.()}
      >
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium">{title}</span>
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

      {/* Markdown Content - Collapsible with smart animation */}
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
            <div className="text-sm leading-relaxed space-y-3 max-h-[60vh] overflow-y-auto pr-2">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ children }) => <h1 className="text-xl font-semibold mb-3">{children}</h1>,
                  h2: ({ children }) => <h2 className="text-lg font-semibold mb-2">{children}</h2>,
                  h3: ({ children }) => <h3 className="text-base font-semibold mb-2">{children}</h3>,
                  p: ({ children }) => <p className="mb-3">{children}</p>,
                  ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
                  li: ({ children }) => <li>{children}</li>,
                  code: ({ className, children }) => {
                    const isInline = !className?.includes('block');
                    return isInline ? (
                      <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>
                    ) : (
                      <code className="bg-muted px-3 py-2 rounded text-xs font-mono block overflow-x-auto">{children}</code>
                    );
                  },
                  pre: ({ children }) => <pre className="bg-muted p-3 rounded mb-3 overflow-x-auto">{children}</pre>,
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-3 border-muted-foreground pl-3 text-muted-foreground mb-3">
                      {children}
                    </blockquote>
                  ),
                  a: ({ href, children }) => (
                    <a href={href} className="text-primary underline" target="_blank" rel="noopener noreferrer">
                      {children}
                    </a>
                  ),
                  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                  em: ({ children }) => <em className="italic">{children}</em>,
                  table: ({ children }) => (
                    <div className="overflow-x-auto my-4">
                      <table className="min-w-full border-collapse border border-border">{children}</table>
                    </div>
                  ),
                  thead: ({ children }) => <thead className="bg-muted">{children}</thead>,
                  tbody: ({ children }) => <tbody>{children}</tbody>,
                  tr: ({ children }) => <tr className="border-b border-border">{children}</tr>,
                  th: ({ children }) => <th className="px-4 py-2 text-left font-semibold">{children}</th>,
                  td: ({ children }) => <td className="px-4 py-2">{children}</td>,
                }}
              >
                {cleanedContent}
              </ReactMarkdown>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});
