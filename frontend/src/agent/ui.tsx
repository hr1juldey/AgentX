/**
 * Widget registry for LangGraph server-driven UI.
 *
 * Maps backend widget types to frontend React components.
 * The LoadExternalComponent uses this registry to render widgets.
 *
 * This file is colocated with graph.ts per C007 architecture.
 *
 * Backend widget types (from designer.py POV generator):
 * - markdown: Text content with markdown formatting
 * - card: Info card with title, content, optional actions
 * - form: Interactive form with fields
 * - progress: Progress indicator
 * - action: Action button
 * - confirmation: Confirmation dialog
 * - voice: Voice interface widget
 * - image: Single image with caption
 * - gallery: Image gallery grid
 * - chart: Data visualization (line, bar, pie, etc.)
 * - searchResult: Search results list
 * - hopProgress: Multi-hop RAG progress
 * - citationCard: Source citation with relevance
 *
 * Shadow DOM: LoadExternalComponent automatically isolates widget styles.
 */

import {
  MarkdownWidget,
  CardWidget,
  FormWidget,
  ProgressWidget,
  ActionWidget,
  ConfirmationWidget,
  VoiceWidget,
  ImageWidget,
  GalleryWidget,
  ChartWidget,
  SearchResultWidget,
  HopProgressWidget,
  CitationCardWidget,
} from '@/components/ui/widgets';

/**
 * Widget component type - accepts any props.
 *
 * Widget components may have specific prop types (e.g., MarkdownWidgetProps)
 * but the registry treats them as flexible components for dynamic rendering.
 */
export type WidgetComponent = React.ComponentType<any>;

/**
 * Widget registry - maps widget type names to React components.
 *
 * Backend uses push_ui_message("card", {...}) which maps to CardWidget here.
 */
export const WIDGET_REGISTRY: Record<string, WidgetComponent> = {
  markdown: MarkdownWidget,
  card: CardWidget,
  form: FormWidget,
  progress: ProgressWidget,
  action: ActionWidget,
  confirmation: ConfirmationWidget,
  voice: VoiceWidget,
  image: ImageWidget,
  gallery: GalleryWidget,
  chart: ChartWidget,
  searchResult: SearchResultWidget,
  hopProgress: HopProgressWidget,
  citationCard: CitationCardWidget,
} as const;

/**
 * All supported widget type names.
 */
export type WidgetType = keyof typeof WIDGET_REGISTRY;

/**
 * Default export for LoadExternalComponent compatibility.
 *
 * LangGraph's LoadExternalComponent expects a default export
 * that maps widget names to components.
 */
export default WIDGET_REGISTRY;

/**
 * Helper function to render a widget with props.
 *
 * Used by LoadExternalComponent or custom rendering logic.
 */
export function renderWidget(type: string, props: Record<string, any>): React.ReactNode {
  const Component = WIDGET_REGISTRY[type];
  if (!Component) {
    console.warn(`Unknown widget type: ${type}`);
    return null;
  }
  return <Component {...props} />;
}

/**
 * Get all registered widget types.
 */
export function getWidgetTypes(): WidgetType[] {
  return Object.keys(WIDGET_REGISTRY) as WidgetType[];
}

/**
 * Check if a widget type is registered.
 */
export function hasWidgetType(type: string): type is WidgetType {
  return type in WIDGET_REGISTRY;
}
