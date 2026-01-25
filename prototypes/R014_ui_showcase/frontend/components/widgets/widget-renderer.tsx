"use client";

import { memo, useMemo } from "react";
import { CollapsibleWidgetWrapper } from "@/components/widgets/collapsible-widget-wrapper";
import { DirectWidgetRenderer } from "@/components/widgets/direct-widget-renderer";
import { WidgetContentRenderer } from "@/lib/widget-content-renderer";
import type { UIDescriptor } from "@/types/widget-types";

// Re-export WidgetContentRenderer for convenience
export { WidgetContentRenderer };

/**
 * WidgetRenderer - Traditional widget renderer with CollapsibleWidgetWrapper
 * Uses DirectWidgetRenderer for all widget types (eliminates need for switch statement)
 *
 * This wrapper adds collapse/expand functionality to widgets in "traditional mode"
 * (non-island mode).
 */
export const WidgetRenderer = memo(function WidgetRenderer({
  descriptor,
  onDismiss,
  onDragEnd,
  onToggleCollapse,
  isExpanded,
}: {
  descriptor: UIDescriptor;
  onDismiss: () => void;
  onDragEnd: (x: number, y: number) => void;
  onToggleCollapse: () => void;
  isExpanded: boolean;
}) {
  const dragPosition = useMemo(
    () =>
      descriptor.x !== undefined || descriptor.y !== undefined
        ? { x: descriptor.x || 0, y: descriptor.y || 0 }
        : undefined,
    [descriptor.x, descriptor.y]
  );

  return (
    <CollapsibleWidgetWrapper
      descriptor={descriptor}
      onDismiss={onDismiss}
      onDragEnd={onDragEnd}
      onToggleCollapse={onToggleCollapse}
      isExpanded={isExpanded}
    >
      <DirectWidgetRenderer
        descriptor={descriptor}
        onDismiss={onDismiss}
        dragPosition={dragPosition}
        onDragEnd={onDragEnd}
      />
    </CollapsibleWidgetWrapper>
  );
});
