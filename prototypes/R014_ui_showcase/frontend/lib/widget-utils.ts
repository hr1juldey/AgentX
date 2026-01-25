import type { UIDescriptor } from "@/types/widget-types";

/**
 * Get widget icon based on type
 * Returns emoji icon for each widget type
 */
export function getWidgetIcon(descriptorType: UIDescriptor["descriptor_type"]): string {
  switch (descriptorType) {
    case "markdown":
      return "📝";
    case "card":
      return "📇";
    case "form":
      return "📋";
    case "progress":
      return "📊";
    case "action":
      return "⚡";
    case "confirmation":
      return "❓";
    case "image":
      return "🖼️";
    case "gallery":
      return "🖼️";
    case "chart":
      return "📈";
    case "search-result":
      return "🔍";
    case "hop-progress":
      return "🔄";
    case "citation-card":
      return "📚";
    default:
      return "📦";
  }
}

/**
 * Get CSS color for widget type based on CSS variables
 * Returns hsl color string for island widget styling
 */
export function getWidgetColor(descriptorType: UIDescriptor["descriptor_type"]): string {
  const colors: Record<string, string> = {
    markdown: "hsl(var(--island-markdown))",
    card: "hsl(var(--island-card))",
    form: "hsl(var(--island-form))",
    progress: "hsl(var(--island-progress))",
    action: "hsl(var(--island-action))",
    confirmation: "hsl(var(--island-confirmation))",
    image: "hsl(var(--island-image))",
    gallery: "hsl(var(--island-gallery))",
    chart: "hsl(var(--island-chart))",
    "search-result": "hsl(var(--island-search-result))",
    "hop-progress": "hsl(var(--island-hop-progress))",
    "citation-card": "hsl(var(--island-citation-card))",
  };
  return colors[descriptorType] || "hsl(var(--island-white))";
}
