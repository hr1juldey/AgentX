"use client";

import { memo } from "react";
import {
  MarkdownWidget,
  CardWidget,
  FormWidget,
  ProgressWidget,
  ActionWidget,
  ConfirmationWidget,
  ImageWidget,
  GalleryWidget,
  ChartWidget,
  SearchResultWidget,
  HopProgressWidget,
  CitationCardWidget,
} from "@/components/widgets";
import type { UIDescriptor } from "@/types/widget-types";

// No-op function for widgets that don't need action handlers
const NOOP_FN = () => {};

interface DirectWidgetRendererProps {
  descriptor: UIDescriptor;
  onDismiss: () => void;
  dragPosition?: { x: number; y: number };
  onDragEnd: (x: number, y: number) => void;
  disableDrag?: boolean; // When true, inner widgets are not draggable (for IsolatedWidget full state)
}

/**
 * DirectWidgetRenderer - Renders widget content without wrapper
 * Used by Island mode for expanded state
 *
 * When disableDrag is true (for IsolatedWidget full state), the inner widget content
 * is NOT draggable - only the outer IsolatedWidget container is draggable.
 */
export const DirectWidgetRenderer = memo(function DirectWidgetRenderer({
  descriptor,
  onDismiss,
  dragPosition,
  onDragEnd,
  disableDrag = false,
}: DirectWidgetRendererProps) {
  // When drag is disabled, pass no-op handlers and don't pass drag position
  const effectiveDragPosition = disableDrag ? undefined : dragPosition;
  const effectiveOnDragEnd = disableDrag ? NOOP_FN : onDragEnd;

  switch (descriptor.descriptor_type) {
    case "markdown":
      return descriptor.content && typeof descriptor.content === "string" ? (
        <MarkdownWidget
          content={descriptor.content}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      ) : null;
    case "card":
      // Handle both mock (string content) and real data (content.cards array)
      let cardContent = "";
      if (typeof descriptor.content === "string") {
        cardContent = descriptor.content;
      } else if ((descriptor.content as any)?.cards) {
        // Convert cards array to markdown for CardWidget
        const cards = (descriptor.content as any).cards;
        if (Array.isArray(cards)) {
          cardContent = cards.map((card: any) => {
            const title = card.title || card.headline || "";
            // Backend uses "value" for metrics, fallback to body/content/description
            const value = card.value ? `**${card.value}**` : "";
            const body = card.body || card.content || card.description || "";
            const source = card.source || card.url ? `*Source: ${card.source || card.url}*` : "";
            // Combine: value (metric) + description
            const cardBody = value ? `${value}\n\n${body}`.trim() : body;
            return `### ${title}\n\n${cardBody}\n\n${source}`;
          }).join("\n\n---\n\n");
        }
      }
      return (
        <CardWidget
          title={descriptor.title}
          content={cardContent}
          actions={descriptor.metadata?.actions as Array<{ label: string; action: string }> | undefined}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "form":
      // Handle both mock (fields array at top level) and real data (content.form_fields)
      const formFields = descriptor.fields
        || (descriptor.content as any)?.form_fields
        || descriptor.form_fields
        || [];
      return (
        <FormWidget
          title={descriptor.title}
          fields={formFields}
          submitLabel={descriptor.submit_button_text}
          onSubmit={NOOP_FN}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "progress":
      // Handle both old (metadata.value) and new (progress_percent at top level) schemas
      const progressValue = descriptor.progress_percent ?? (descriptor.metadata?.value as number | undefined);
      const progressText = descriptor.status_text ?? (descriptor.metadata?.status_text as string | undefined);
      return (
        <ProgressWidget
          title={descriptor.title}
          value={progressValue}
          statusText={progressText}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "action":
      return (
        <ActionWidget
          title={descriptor.title}
          content={typeof descriptor.content === "string" ? descriptor.content : undefined}
          buttonText={descriptor.button_text}
          onAction={NOOP_FN}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "confirmation":
      return (
        <ConfirmationWidget
          title={descriptor.title}
          message={descriptor.message || ""}
          confirmLabel={descriptor.confirm_label}
          cancelLabel={descriptor.cancel_label}
          variant="destructive"
          onConfirm={NOOP_FN}
          onCancel={NOOP_FN}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "image":
      return (
        <ImageWidget
          title={descriptor.title}
          content={typeof descriptor.content === "string" ? descriptor.content : undefined}
          caption={descriptor.metadata?.caption as string | undefined}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "gallery":
      return (
        <GalleryWidget
          title={descriptor.title}
          content={typeof descriptor.content === "string" ? descriptor.content : undefined}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "chart":
      // Handle both mock (metadata.data) and real data (content.data object)
      const chartContent = descriptor.content as any;
      const chartData = chartContent?.data
        || descriptor.metadata?.data
        || [];
      const chartType = chartContent?.type
        || descriptor.metadata?.chartType as "bar" | "line" | "pie" | undefined
        || "bar";
      const chartTitle = chartContent?.title || descriptor.title;
      // Extract colors from backend (domain-appropriate colors)
      const chartColors = chartContent?.colors
        || (descriptor.metadata?.colors as string[] | undefined)
        || undefined;
      return (
        <ChartWidget
          title={chartTitle}
          content={typeof chartContent === "string" ? chartContent : undefined}
          chartType={chartType}
          data={chartData}
          colors={chartColors}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "search-result":
      return (
        <SearchResultWidget
          content={typeof descriptor.content === "string" ? descriptor.content : ""}
          citations={descriptor.citations}
          metadata={descriptor.metadata}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "hop-progress":
      return (
        <HopProgressWidget
          events={descriptor.hop_events || []}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "citation-card":
      return (
        <CitationCardWidget
          citations={descriptor.citations || []}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    default:
      return null;
  }
});
