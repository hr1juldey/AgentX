"use client";

import { Card, CardContent } from "@/components/ui/card";
import { MessageSquare } from "lucide-react";
import { AnimatePresence, LayoutGroup } from "framer-motion";
import { MobileBubbleLayer, IslandModeWidgets } from "@/components/islands";
import { WidgetRenderer } from "@/components/widgets/widget-renderer";
import type { UIDescriptor } from "@/types/widget-types";

interface MainViewProps {
  enableIslands: boolean;
  emptyExpandedIds: React.MutableRefObject<Set<string>>;
  stableEmptyExpandFn: React.MutableRefObject<() => void>;
  onWidgetDelete: (id: string) => void;
  storeWidgetIds: string[];
  widgets: UIDescriptor[];
  getWidgetHandlers: (id: string) => {
    onDismiss: () => void;
    onDragEndCompat: (x: number, y: number) => void;
    onToggleCollapse: () => void;
  };
}

/**
 * MainView - Main workspace view displaying generated widgets
 *
 * Supports two modes:
 * - Island mode: Uses Zustand store with IsolatedWidget (no AnimatePresence wrapper)
 * - Traditional mode: Uses CollapsibleWidgetWrapper with AnimatePresence transitions
 */
export function MainView({
  enableIslands,
  emptyExpandedIds,
  stableEmptyExpandFn,
  onWidgetDelete,
  storeWidgetIds,
  widgets,
  getWidgetHandlers,
}: MainViewProps) {
  return (
    <div className="space-y-6 relative">
      {/* Mobile Bubble Layer - visible only on mobile */}
      {/* NOTE: With State Colocation, widgets track their own state.
          MobileBubbleLayer simplified - parent no longer tracks widget states. */}
      {enableIslands && (
        <MobileBubbleLayer
          expandedIds={emptyExpandedIds.current}
          onExpand={stableEmptyExpandFn.current}
          onDismiss={onWidgetDelete}
        />
      )}

      {/* Generated Widgets - 3-State Cycle System (Island -> Card -> Full) */}
      {enableIslands ? (
        // Island UI mode - use Zustand store with IsolatedWidget
        // CRITICAL: No AnimatePresence/LayoutGroup wrapper for island mode
        // These can cause visual resets when widgets are added/removed
        // Each IsolatedWidget handles its own animations internally
        <IslandModeWidgets widgetIds={storeWidgetIds} />
      ) : (
        // Traditional mode (CollapsibleWidgetWrapper) - use controlled isExpanded
        // Keep AnimatePresence for traditional mode smooth transitions
        <LayoutGroup>
          <AnimatePresence mode="popLayout">
            {widgets.map((widget) => {
              const handlers = getWidgetHandlers(widget.descriptor_id);
              return (
                <WidgetRenderer
                  key={widget.descriptor_id}
                  descriptor={widget}
                  onDismiss={handlers.onDismiss}
                  onDragEnd={handlers.onDragEndCompat}
                  onToggleCollapse={handlers.onToggleCollapse}
                  isExpanded={!widget.collapsed}
                />
              );
            })}
          </AnimatePresence>
        </LayoutGroup>
      )}

      {(!enableIslands && widgets.length === 0) && (
        <Card className="border-dashed">
          <CardContent className="py-12 text-center">
            <MessageSquare className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
            <p className="text-muted-foreground">
              No widgets yet. Click the Central Island button below to generate your first widget.
            </p>
          </CardContent>
        </Card>
      )}

      {enableIslands && storeWidgetIds.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="py-12 text-center">
            <MessageSquare className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
            <p className="text-muted-foreground">
              No widgets yet. Click the Central Island button below to generate your first widget.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
