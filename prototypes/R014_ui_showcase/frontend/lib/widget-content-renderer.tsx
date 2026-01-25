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

  // These widget types have markdown content (when content is actually a string)
  const markdownTypes = ["markdown", "card", "search-result", "citation-card"];

  // Special case for card: real backend sends content as object {cards: [...]}
  // Only treat as markdown if content is actually a string
  if (descriptor_type === "card") {
    return typeof content === "string" && content.trim().length > 0;
  }

  return markdownTypes.includes(descriptor_type) && typeof content === "string";
}

/**
 * Get content preview based on widget type
 * Returns string for all widget types
 */
function getWidgetContentPreview(widget: UIDescriptor): string {
  const { descriptor_type, content, title, form_fields, progress_percent, status_text } = widget;

  // Structured widgets - handle object content first
  switch (descriptor_type) {
    case "form":
      // Backend uses `form_fields` array, not `fields`
      // Each field has: label, type, description, required, options
      return `${form_fields?.length || 0} form fields • ${widget.submit_button_text || "Submit"}`;

    case "chart":
      // Real backend: content = {title, type, data, x_axis, y_axis}
      return `Chart • ${(content as any)?.title || title || "Visualization"}`;

    case "card":
      // Real backend: content = {cards: [...]}
      // Mock data: content = string (markdown)
      if (typeof content === "string" && content.trim()) {
        return content;
      }
      return `${(content as any)?.cards?.length || 0} cards • ${title || ""}`;

    case "progress":
      return `${progress_percent || 0}% complete${status_text ? ` • ${status_text}` : ""}`;

    case "action":
      return (content as any)?.label || title || "Action";

    case "confirmation":
      return (content as any)?.message || title || "Confirm action";

    case "image":
      // Real backend: content = [urls] (array)
      if (Array.isArray(content)) {
        return `${content.length} images • ${title || ""}`;
      }
      return `Image • ${title || ""}`;

    case "gallery":
      // Real backend: content = [{title, url, ...}] (array)
      if (Array.isArray(content)) {
        return `Gallery • ${content.length} items`;
      }
      return `Gallery • ${(content as any)?.images?.length || 0} items`;

    case "hop-progress":
      return `Progress • ${title || ""}`;

    default:
      // String-based widgets (markdown, search-result, citation-card)
      if (typeof content === "string" && content.trim()) {
        return content;
      }
      return title || descriptor_type;
  }
}
