"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { UIDescriptor } from "@/types/widget-types";

interface ContentRendererProps {
  widget: UIDescriptor;
  className?: string;
}

/**
 * Safely renders widget content based on widget type
 * Handles both string content (markdown) and structured content (form, chart, etc.)
 */
export function WidgetContentRenderer({ widget, className = "" }: ContentRendererProps) {
  const content = getWidgetContentPreview(widget);

  if (isMarkdownContent(widget, content)) {
    // String content - render as markdown
    return (
      <div className={className}>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </div>
    );
  }

  // Structured content - render as text preview
  return (
    <div className={className}>
      <p className="text-sm text-muted-foreground">{content}</p>
    </div>
  );
}

/**
 * Check if widget content should be rendered as markdown
 */
function isMarkdownContent(widget: UIDescriptor, content: string): boolean {
  const { descriptor_type } = widget;

  // These widget types have markdown content
  const markdownTypes = ["markdown", "card", "search-result", "citation-card"];
  return markdownTypes.includes(descriptor_type) && typeof content === "string";
}

/**
 * Get content preview based on widget type
 * Returns string for all widget types
 */
function getWidgetContentPreview(widget: UIDescriptor): string {
  const { descriptor_type, content, title, form_fields, progress_percent, status_text } = widget;

  // String-based widgets with actual content
  if (typeof content === "string" && content.trim()) {
    return content;
  }

  // Structured widgets - provide summary
  switch (descriptor_type) {
    case "form":
      // Backend uses `form_fields` array, not `fields`
      // Each field has: label, type, description, required, options
      return `${form_fields?.length || 0} form fields • ${widget.submit_button_text || "Submit"}`;

    case "chart":
      return `Chart • ${title || "Visualization"}`;

    case "progress":
      return `${progress_percent || 0}% complete${status_text ? ` • ${status_text}` : ""}`;

    case "action":
      return (content as any)?.label || title || "Action";

    case "confirmation":
      return (content as any)?.message || title || "Confirm action";

    case "image":
      return `Image • ${title || ""}`;

    case "gallery":
      return `Gallery • ${(content as any)?.images?.length || 0} items`;

    case "hop-progress":
      return `Progress • ${title || ""}`;

    default:
      return title || descriptor_type;
  }
}
