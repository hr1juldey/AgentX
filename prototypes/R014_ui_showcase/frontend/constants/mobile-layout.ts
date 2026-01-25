import {
  FileText,
  Layout,
  ClipboardList,
  BarChart3,
  Zap,
  HelpCircle,
  Image as ImageIcon,
  Images,
  LineChart,
  type LucideIcon,
} from "lucide-react";

/**
 * Mobile layout constants for bubble layer
 */
export const MOBILE_LAYOUT = {
  BUBBLE_SIZE: 48, // 48px for mobile (vs 56px desktop)
  MAX_BUBBLES: 6,
  BUBBLE_SPACING: 60,
  EDGE_MARGIN: 16,
  MAX_EXPANDED_MOBILE: 4,
} as const;

/**
 * Widget type to Lucide icon component mapping
 * Used by MobileBubbleLayer for rendering icons
 */
export const WIDGET_LUCIDE_ICONS: Record<string, LucideIcon> = {
  markdown: FileText,
  card: Layout,
  form: ClipboardList,
  progress: BarChart3,
  action: Zap,
  confirmation: HelpCircle,
  image: ImageIcon,
  gallery: Images,
  chart: LineChart,
};

/**
 * Widget type to CSS color variable mapping (using var() for CSS variables)
 * Used by MobileBubbleLayer for bubble colors
 */
export const WIDGET_CSS_COLORS: Record<string, string> = {
  markdown: "var(--island-markdown)",
  card: "var(--island-card)",
  form: "var(--island-form)",
  progress: "var(--island-progress)",
  action: "var(--island-action)",
  confirmation: "var(--island-confirmation)",
  image: "var(--island-image)",
  gallery: "var(--island-gallery)",
  chart: "var(--island-chart)",
};
