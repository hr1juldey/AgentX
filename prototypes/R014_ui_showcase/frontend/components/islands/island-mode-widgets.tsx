"use client";

import { memo } from "react";
import { IsolatedWidget } from "@/components/widgets/isolated-widget";

/**
 * IslandModeWidgets - Memoized container for island mode widgets
 *
 * CRITICAL: This component isolates widget rendering from parent re-renders.
 * When HomePage re-renders (due to widgetIds changing), THIS component
 * will also re-render, BUT the IsolatedWidget children will NOT re-render
 * because they are memoized and their props (descriptorId) haven't changed.
 */
export const IslandModeWidgets = memo(function IslandModeWidgets({
  widgetIds,
}: {
  widgetIds: string[];
}) {
  return (
    <>
      {widgetIds.map((id) => (
        <IsolatedWidget key={id} descriptorId={id} />
      ))}
    </>
  );
}, (prevProps, nextProps) => {
  // Custom comparison: only re-render if widgetIds array changed
  // This uses array comparison since widgetIds should be a stable reference from Zustand
  const prevIds = prevProps.widgetIds;
  const nextIds = nextProps.widgetIds;

  // Fast path: same reference
  if (prevIds === nextIds) return true;

  // Length changed
  if (prevIds.length !== nextIds.length) return false;

  // Check if any ID changed (order matters for stable rendering)
  for (let i = 0; i < prevIds.length; i++) {
    if (prevIds[i] !== nextIds[i]) return false;
  }

  // All IDs match - skip re-render
  return true;
});
