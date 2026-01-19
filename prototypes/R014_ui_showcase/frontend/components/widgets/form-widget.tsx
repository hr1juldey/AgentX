"use client"

import { motion } from "framer-motion"
import { X } from "lucide-react"
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
  onDismiss?: () => void
}

export function FormWidget({ title, content, fields, submitLabel = "Submit", onSubmit, onDismiss }: FormWidgetProps) {
  const handleSubmit = (e: React.FormEvent) => {
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
      <form onSubmit={handleSubmit} className="space-y-4">
        {title && <h3 className="text-lg font-semibold">{title}</h3>}
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
    </motion.div>
  )
}
