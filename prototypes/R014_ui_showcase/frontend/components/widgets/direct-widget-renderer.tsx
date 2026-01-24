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

// No-op function for widgets that don't need action handlers
const NOOP_FN = () => {};

interface UIDescriptor {
  descriptor_id: string;
  descriptor_type: string;
  title?: string;
  content?: string;
  fields?: Array<{ name: string; type: string; label: string; required: boolean; options?: string[] }>;
  submit_button_text?: string;
  task_name?: string;
  progress_percent?: number;
  status_text?: string;
  button_text?: string;
  action_id?: string;
  message?: string;
  confirm_label?: string;
  cancel_label?: string;
  dismissible?: boolean;
  x?: number;
  y?: number;
  collapsed?: boolean;
  id?: string;
  metadata?: Record<string, unknown>;
  citations?: Array<Record<string, unknown>>;
  hop_events?: Array<Record<string, unknown>>;
}

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
          title={descriptor.title}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      ) : null;
    case "card":
      return (
        <CardWidget
          title={descriptor.title || ""}
          content={descriptor.content || ""}
          actions={[]}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "form":
      return (
        <FormWidget
          title={descriptor.title}
          fields={descriptor.fields || []}
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
          title={descriptor.title || "Processing"}
          value={(descriptor.progress_percent || 0) / 100}
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
          buttonText={descriptor.button_text || "Action"}
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
          title={descriptor.title || "Confirm"}
          message={descriptor.message || ""}
          confirmLabel={descriptor.confirm_label}
          cancelLabel={descriptor.cancel_label}
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
          caption={descriptor.content}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          descriptor_id={descriptor.descriptor_id}
          disableDrag={disableDrag}
        />
      );
    case "gallery":
      return (
        <GalleryWidget
          title={descriptor.title}
          content={descriptor.content}
          images={descriptor.metadata?.images as Array<{ url: string; caption?: string; title?: string }> | undefined}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          descriptor_id={descriptor.descriptor_id}
          disableDrag={disableDrag}
        />
      );
    case "chart":
      return (
        <ChartWidget
          title={descriptor.title}
          content={descriptor.content}
          chartType={(descriptor.metadata?.chart_type as "bar" | "line" | "pie" | "area") || "bar"}
          data={descriptor.metadata?.data as Array<Record<string, string | number>>}
          dataKeys={descriptor.metadata?.data_keys as string[]}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "search-result":
      return descriptor.content ? (
        <SearchResultWidget
          content={descriptor.content}
          citations={descriptor.citations as any}
          metadata={descriptor.metadata}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      ) : null;
    case "hop-progress":
      return (
        <HopProgressWidget
          events={descriptor.hop_events as any || []}
          onDismiss={onDismiss}
          dragPosition={effectiveDragPosition}
          onDragEnd={effectiveOnDragEnd}
          disableDrag={disableDrag}
        />
      );
    case "citation-card":
      return (
        <CitationCardWidget
          citations={descriptor.citations as any || []}
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
