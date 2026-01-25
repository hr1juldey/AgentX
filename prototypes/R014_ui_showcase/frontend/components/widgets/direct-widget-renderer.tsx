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
      return descriptor.content ? (
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
            const body = card.body || card.content || card.description || "";
            const source = card.source || card.url ? `*Source: ${card.source || card.url}*` : "";
            return `### ${title}\n\n${body}\n\n${source}`;
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
      return (
        <ProgressWidget
          title={descriptor.title}
          value={descriptor.progress_percent}
          statusText={descriptor.status_text}
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
          content={descriptor.content}
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
          content={descriptor.content}
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
          content={descriptor.content}
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
      return (
        <ChartWidget
          title={chartTitle}
          content={typeof chartContent === "string" ? chartContent : undefined}
          chartType={chartType}
          data={chartData}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "search-result":
      return (
        <SearchResultWidget
          content={descriptor.content || ""}
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
