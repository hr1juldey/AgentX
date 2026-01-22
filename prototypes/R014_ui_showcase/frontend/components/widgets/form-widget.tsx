"use client"
import { memo, useCallback } from "react"

import { motion, AnimatePresence } from "framer-motion"
import { X, FileEdit, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

interface FormWidgetProps {
  title?: string
  content?: string
  fields?: Array<{ name: string; type: string; label: string; placeholder?: string; options?: string[] }>
  submitLabel?: string
  onSubmit?: (data: Record<string, string>) => void
  collapsed?: boolean
  onToggleCollapse?: () => void
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
}

export const FormWidget = memo(function FormWidget({
  title,
  content,
  fields,
  submitLabel = "Submit",
  onSubmit,
  collapsed = false,
  onToggleCollapse,
  onDismiss,
  dragPosition,
  onDragEnd
}: FormWidgetProps) {
  const handleDragEnd = useCallback((_: any, info: any) => {
    onDragEnd?.(
      (dragPosition?.x || 0) + info.offset.x,
      (dragPosition?.y || 0) + info.offset.y
    );
  }, [onDragEnd, dragPosition]);

  const handleDismiss = useCallback(() => {
    onDismiss?.();
  }, [onDismiss]);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = Object.fromEntries(formData)
    onSubmit?.(data as Record<string, string>)
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.25 }}
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
      className="relative bg-card border border-border rounded-lg cursor-grab shadow-lg hover:shadow-xl"
    >
      {/* Widget Header - Click to toggle (Jira-style) */}
      <div
        className="flex items-center justify-between px-4 py-2 border-b bg-muted/30 cursor-pointer hover:bg-muted/50"
        onClick={() => onToggleCollapse?.()}
      >
        <div className="flex items-center gap-2">
          <FileEdit className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium">{title || "Form"}</span>
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

      {/* Form Content - Collapsible with smart animation */}
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
              <form onSubmit={handleSubmit} className="space-y-4">
                {content && <p className="text-sm text-muted-foreground">{content}</p>}

                {fields?.map((field) => (
                  <div key={field.name} className="space-y-2">
                    <Label htmlFor={field.name}>{field.label}</Label>
                    {field.type === "textarea" ? (
                      <Textarea
                        id={field.name}
                        name={field.name}
                        placeholder={field.placeholder}
                        className="min-h-[100px]"
                      />
                    ) : field.type === "select" ? (
                      <select
                        id={field.name}
                        name={field.name}
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      >
                        <option value="">Select...</option>
                        {field.options?.map((opt) => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                    ) : (
                      <Input
                        id={field.name}
                        name={field.name}
                        type={field.type}
                        placeholder={field.placeholder}
                      />
                    )}
                  </div>
                ))}

                <Button type="submit" className="w-full">
                  {submitLabel}
                </Button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
});
