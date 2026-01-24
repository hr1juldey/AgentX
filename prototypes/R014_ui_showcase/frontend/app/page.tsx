"use client";

import { useState, useEffect, useCallback, useMemo, memo, useRef, startTransition } from "react";
import { motion, AnimatePresence, PanInfo, LayoutGroup } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Plus, MessageSquare, X, Sparkles, Images, History, Database, ChevronDown, Minimize2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ThemeToggle } from "@/components/showcase/theme-toggle";
import { QAProgressDisplay } from "@/components/ui/qa-progress";
import { CentralIsland } from "@/components/ui/central-island";
import { MarkdownWidget } from "@/components/widgets/markdown-widget";
import { CardWidget } from "@/components/widgets/card-widget";
import { FormWidget } from "@/components/widgets/form-widget";
import { ProgressWidget } from "@/components/widgets/progress-widget";
import { ActionWidget } from "@/components/widgets/action-widget";
import { ConfirmationWidget } from "@/components/widgets/confirmation-widget";
import { ImageWidget } from "@/components/widgets/image-widget";
import { GalleryWidget } from "@/components/widgets/gallery-widget";
import { ChartWidget } from "@/components/widgets/chart-widget";
import { SearchResultWidget } from "@/components/widgets/search-result-widget";
import { HopProgressWidget } from "@/components/widgets/hop-progress-widget";
import { CitationCardWidget } from "@/components/widgets/citation-card-widget";
import { ToolIsland, MobileBubbleLayer } from "@/components/islands";

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
  // Position tracking for draggable widgets
  x?: number;
  y?: number;
  // Collapsible widget state
  collapsed?: boolean;
  // Backend response fields
  id?: string;
  type?: string;
  timestamp?: string;
  metadata?: Record<string, unknown>;
  // Multi-hop search optional fields
  progress?: number;
  hops_completed?: number;
  total_hops?: number;
  reflection_reasoning?: string;
  citations?: Array<{
    cited_text: string;
    document_index: number;
    document_title?: string;
    url?: string;
  }>;
  hop_events?: Array<{
    event_type: string;
    hop_number: number;
    total_hops: number;
    message: string;
    progress: number;
    eta_seconds?: number;
    documents_found?: number;
    query_used?: string;
    reflection_reasoning?: string;
  }>;
  eta_seconds?: number;
}

interface Session {
  id?: string;
  session_id?: string;
  title: string;
  created_at?: string;
  date?: string;
}

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8014";
const appName = process.env.NEXT_PUBLIC_APP_NAME || "R014 UI Showcase";

// Stable no-op functions to prevent re-renders (identity-stable across renders)
const NOOP_FN = () => {};
const NOOP_DRAG_FN = (_x: number, _y: number) => {};
const STOP_PROPAGATION = (e: React.MouseEvent) => e.stopPropagation();

// UI boundaries to prevent widgets from spawning over fixed UI elements
const UI_BOUNDARIES = {
  HEADER_HEIGHT: 56,
  SIDEBAR_WIDTH: 320,
  CENTRAL_ISLAND_MARGIN: 120, // bottom margin to avoid central island
  EDGE_PADDING: 20,
  ISLAND_DIAMETER: 56,
};

// Calculate safe spawn zones that respect UI boundaries
const getSafeSpawnZone = (sidebarOpen: boolean) => {
  const vw = typeof window !== "undefined" ? window.innerWidth : 1200;
  const vh = typeof window !== "undefined" ? window.innerHeight : 800;

  return {
    left: {
      minX: (sidebarOpen ? UI_BOUNDARIES.SIDEBAR_WIDTH : 0) + UI_BOUNDARIES.EDGE_PADDING,
      maxX: vw * 0.45,
      minY: UI_BOUNDARIES.HEADER_HEIGHT + UI_BOUNDARIES.EDGE_PADDING,
      maxY: vh - UI_BOUNDARIES.CENTRAL_ISLAND_MARGIN,
    },
    right: {
      minX: vw * 0.55,
      maxX: vw - UI_BOUNDARIES.ISLAND_DIAMETER - UI_BOUNDARIES.EDGE_PADDING,
      minY: UI_BOUNDARIES.HEADER_HEIGHT + UI_BOUNDARIES.EDGE_PADDING,
      maxY: vh - UI_BOUNDARIES.CENTRAL_ISLAND_MARGIN,
    },
  };
};

type View = "main" | "gallery" | "sessions" | "connectors";

// Widget 3-State Renderer - handles Island -> Card -> Full cycle
// All states are clickable (cycles), draggable, text selectable
const Widget3StateRenderer = memo(function Widget3StateRenderer({
  widget,
  state,
  position,
  zIndex,
  onCycleState,
  onDragEnd,
  onDismiss,
}: {
  widget: UIDescriptor;
  state: "island" | "card" | "full";
  position: { x: number; y: number };
  zIndex: number;
  onCycleState: () => void;
  onDragEnd: (x: number, y: number) => void;
  onDismiss: () => void;
}) {
  // Track drag distance to distinguish clicks from drags
  const dragDistanceRef = useRef(0);
  const CLICK_THRESHOLD = 5;

  const handleDrag = useCallback(() => {
    dragDistanceRef.current++;
  }, []);

  const handleClick = useCallback(() => {
    if (dragDistanceRef.current < CLICK_THRESHOLD) {
      onCycleState();
    }
    dragDistanceRef.current = 0;
  }, [onCycleState]);

  const handleDragEnd = useCallback((_: unknown, info: PanInfo) => {
    onDragEnd(info.offset.x, info.offset.y);
    dragDistanceRef.current = 0;
  }, [onDragEnd]);

  // Memoized dismiss handler that stops propagation
  const handleDismissClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    onDismiss();
  }, [onDismiss]);

  // Get widget icon based on type
  const getWidgetIcon = () => {
    switch (widget.descriptor_type) {
      case "markdown": return "📝";
      case "card": return "📇";
      case "form": return "📋";
      case "progress": return "📊";
      case "action": return "⚡";
      case "confirmation": return "❓";
      case "image": return "🖼️";
      case "gallery": return "🖼️";
      case "chart": return "📈";
      case "search-result": return "🔍";
      case "hop-progress": return "🔄";
      case "citation-card": return "📚";
      default: return "📦";
    }
  };

  // Get color for widget type
  const getWidgetColor = () => {
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
    return colors[widget.descriptor_type] || "hsl(var(--island-white))";
  };

  const widgetColor = getWidgetColor();

  // Capture state for indicators to avoid type narrowing issues
  const currentState = state;

  return (
    <AnimatePresence mode="wait">
      {state === "island" && (
        <ToolIsland
          key="island"
          widget={widget}
          position={position}
          isActive={false}
          onClick={onCycleState}
          onDragEnd={onDragEnd}
        />
      )}

      {state === "card" && (
        <motion.div
          key="card"
          drag
          dragElastic={0}
          dragMomentum={false}
          whileDrag={{ cursor: "grabbing", scale: 1.02 }}
          onDrag={handleDrag}
          onDragEnd={handleDragEnd}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.22 }}
          className="fixed pointer-events-auto"
          style={{ x: position.x, y: position.y, position: "fixed", zIndex }}
        >
          <motion.div
            className="relative group cursor-pointer select-text"
            onClick={handleClick}
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            {/* Card container */}
            <motion.div
              className="rounded-2xl shadow-2xl backdrop-blur-md bg-card/95 border border-border/50 overflow-hidden"
              style={{ width: 320 }}
              whileHover={{ boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.4)" }}
            >
              {/* Header with icon, title, and cycle indicator */}
              <div className="flex items-center gap-3 p-4 border-b border-border/50" style={{ background: widgetColor }}>
                <span className="text-2xl">{getWidgetIcon()}</span>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm text-white truncate select-text">
                    {widget.title || widget.descriptor_type}
                  </h3>
                </div>
                {/* Cycle indicator */}
                <div className="flex gap-1">
                  <div className={`w-1.5 h-1.5 rounded-full ${currentState === "island" ? "bg-white" : "bg-white/30"}`} />
                  <div className={`w-1.5 h-1.5 rounded-full ${currentState === "card" ? "bg-white" : "bg-white/30"}`} />
                  <div className={`w-1.5 h-1.5 rounded-full ${currentState === "full" ? "bg-white" : "bg-white/30"}`} />
                </div>
              </div>

              {/* Content summary with markdown rendering */}
              <div className="p-4 overflow-hidden">
                <div className="text-sm text-foreground/80 line-clamp-3 select-text prose prose-sm max-w-none dark:prose-invert [&>*]:mb-0 [&>*]:mt-0 [&_p]:inline [&_ul]:inline [&_ol]:inline [&_li]:inline">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {widget.content || "Click to expand"}
                  </ReactMarkdown>
                </div>
              </div>

              {/* Footer with hint */}
              <div className="px-4 py-2 bg-muted/50 border-t border-border/50">
                <p className="text-xs text-muted-foreground text-center">
                  Click to expand • Drag to move
                </p>
              </div>
            </motion.div>

            {/* Dismiss button */}
            <button
              onClick={handleDismissClick}
              className="absolute -top-2 -right-2 p-1.5 rounded-full bg-destructive text-destructive-foreground opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity shadow-lg"
              aria-label="Dismiss widget"
            >
              <X className="w-3 h-3" />
            </button>
          </motion.div>
        </motion.div>
      )}

      {state === "full" && (
        <motion.div
          key="full"
          drag
          dragElastic={0}
          dragMomentum={false}
          whileDrag={{ cursor: "grabbing" }}
          onDrag={handleDrag}
          onDragEnd={handleDragEnd}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.22 }}
          className="fixed pointer-events-auto"
          style={{ x: position.x, y: position.y, position: "fixed", zIndex }}
        >
          <div className="relative group">
            {/* Integrated header with cycle button */}
            <motion.div
              className="flex items-center gap-3 px-4 py-3 rounded-t-2xl border-b border-border/50 select-text"
              style={{ background: widgetColor }}
              onClick={handleClick}
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.99 }}
            >
              <span className="text-2xl">{getWidgetIcon()}</span>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-base text-white truncate select-text">
                  {widget.title || widget.descriptor_type}
                </h3>
              </div>
              {/* Cycle indicator */}
              <div className="flex gap-1 mr-2">
                <div className={`w-1.5 h-1.5 rounded-full ${currentState === "island" ? "bg-white" : "bg-white/30"}`} />
                <div className={`w-1.5 h-1.5 rounded-full ${currentState === "card" ? "bg-white" : "bg-white/30"}`} />
                <div className={`w-1.5 h-1.5 rounded-full ${currentState === "full" ? "bg-white" : "bg-white/30"}`} />
              </div>
              {/* Integrated cycle button (Minimize2 icon) */}
              <Minimize2 className="w-4 h-4 text-white/70" />
            </motion.div>

            {/* Content - pass no-op dismiss to prevent accidental deletion */}
            <div
              className="rounded-b-2xl shadow-2xl backdrop-blur-md bg-card/95 border border-t-0 border-border/50 overflow-hidden select-text"
              onClick={STOP_PROPAGATION}
            >
              <DirectWidgetRenderer
                descriptor={widget}
                onDismiss={NOOP_FN}  // No-op - dismiss only via top-right button
                dragPosition={{ x: 0, y: 0 }}
                onDragEnd={NOOP_DRAG_FN}
              />
            </div>

            {/* Dismiss button */}
            <button
              onClick={handleDismissClick}
              className="absolute top-16 right-2 p-2 rounded-full bg-destructive text-destructive-foreground opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity shadow-lg"
              aria-label="Dismiss widget"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
});

// Widget content renderer without wrapper (for Island mode)
// Island mode uses expandedPanelIds for collapse, so widgets are always fully shown
const DirectWidgetRenderer = memo(function DirectWidgetRenderer({
  descriptor,
  onDismiss,
  dragPosition,
  onDragEnd,
}: {
  descriptor: UIDescriptor;
  onDismiss: () => void;
  dragPosition?: { x: number; y: number };
  onDragEnd: (x: number, y: number) => void;
}) {
  switch (descriptor.descriptor_type) {
    case "markdown":
      return descriptor.content ? (
        <MarkdownWidget
          content={descriptor.content}
          title={descriptor.title}
          onDismiss={onDismiss}
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
        />
      ) : null;
    case "card":
      return (
        <CardWidget
          title={descriptor.title || ""}
          content={descriptor.content || ""}
          actions={[]}
          onDismiss={onDismiss}
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
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
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
        />
      );
    case "progress":
      return (
        <ProgressWidget
          title={descriptor.title || "Processing"}
          value={(descriptor.progress_percent || 0) / 100}
          statusText={descriptor.status_text}
          onDismiss={onDismiss}
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
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
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
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
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
        />
      );
    case "image":
      return (
        <ImageWidget
          title={descriptor.title}
          content={descriptor.content}
          caption={descriptor.content}
          onDismiss={onDismiss}
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
          descriptor_id={descriptor.descriptor_id}
        />
      );
    case "gallery":
      return (
        <GalleryWidget
          title={descriptor.title}
          content={descriptor.content}
          images={descriptor.metadata?.images as Array<{ url: string; caption?: string; title?: string }> | undefined}
          onDismiss={onDismiss}
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
          descriptor_id={descriptor.descriptor_id}
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
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
        />
      );
    case "search-result":
      return descriptor.content ? (
        <SearchResultWidget
          content={descriptor.content}
          citations={descriptor.citations}
          metadata={descriptor.metadata}
          onDismiss={onDismiss}
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
        />
      ) : null;
    case "hop-progress":
      return (
        <HopProgressWidget
          events={descriptor.hop_events || []}
          onDismiss={onDismiss}
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
        />
      );
    case "citation-card":
      return (
        <CitationCardWidget
          citations={descriptor.citations || []}
          onDismiss={onDismiss}
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
        />
      );
    default:
      return null;
  }
});

// Collapsible wrapper for widgets - uses controlled component pattern (FIXED)
const CollapsibleWidgetWrapper = memo(function CollapsibleWidgetWrapper({
  descriptor,
  onDismiss,
  onDragEnd,
  onToggleCollapse,
  isExpanded, // NEW: Controlled by parent
  children,
}: {
  descriptor: UIDescriptor;
  onDismiss: () => void;
  onDragEnd: (x: number, y: number) => void;
  onToggleCollapse: () => void;
  isExpanded: boolean; // NEW: Controlled prop
  children: React.ReactNode;
}) {
  // Widget type icons
  const getWidgetIcon = useCallback(() => {
    switch (descriptor.descriptor_type) {
      case "markdown": return "📝";
      case "card": return "📇";
      case "form": return "📋";
      case "progress": return "📊";
      case "action": return "⚡";
      case "confirmation": return "❓";
      case "image": return "🖼️";
      case "gallery": return "🖼️";
      case "chart": return "📈";
      case "search-result": return "🔍";
      case "hop-progress": return "🔄";
      case "citation-card": return "📚";
      default: return "📦";
    }
  }, [descriptor.descriptor_type]);

  // Memoized handlers to prevent re-renders
  const handleCollapsedDragEnd = useCallback((_: unknown, info: PanInfo) => {
    onDragEnd(
      (descriptor.x || 0) + info.offset.x,
      (descriptor.y || 0) + info.offset.y
    );
  }, [onDragEnd, descriptor.x, descriptor.y]);

  const handleDismissClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    onDismiss();
  }, [onDismiss]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
    >
      {/* Collapsed mini island */}
      <AnimatePresence mode="wait">
        {!isExpanded ? (
          <motion.div
            key="collapsed"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="relative"
          >
            <motion.button
              drag
              dragElastic={0.2}
              dragMomentum={false}
              dragConstraints={{ left: -500, right: 500, top: -500, bottom: 500 }}
              whileDrag={{ scale: 1.05, cursor: "grabbing", zIndex: 50 }}
              onDragEnd={handleCollapsedDragEnd}
              onClick={onToggleCollapse}
              style={{ x: descriptor.x || 0, y: descriptor.y || 0 }}
              className="relative bg-card border border-border rounded-full cursor-grab shadow-lg hover:shadow-xl px-4 py-2 flex items-center gap-2 hover:bg-muted/50 transition-colors"
            >
              <span className="text-lg">{getWidgetIcon()}</span>
              <span className="text-sm font-medium truncate max-w-[120px]">
                {descriptor.title || descriptor.descriptor_type}
              </span>
              {/* Dismiss button */}
              <button
                onClick={handleDismissClick}
                className="p-1 rounded-full hover:bg-destructive/10 hover:text-destructive transition-colors"
                aria-label="Dismiss"
              >
                <X className="w-3 h-3" />
              </button>
            </motion.button>
          </motion.div>
        ) : (
          <motion.div
            key="expanded"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});

// Traditional widget renderer with CollapsibleWidgetWrapper
const WidgetRenderer = memo(function WidgetRenderer({
  descriptor,
  onDismiss,
  onDragEnd,
  onToggleCollapse,
  isExpanded, // NEW: Controlled prop
}: {
  descriptor: UIDescriptor;
  onDismiss: () => void;
  onDragEnd: (x: number, y: number) => void;
  onToggleCollapse: () => void;
  isExpanded: boolean; // NEW: Controlled prop
}) {
  const dragPosition = useMemo(
    () =>
      descriptor.x !== undefined || descriptor.y !== undefined
        ? { x: descriptor.x || 0, y: descriptor.y || 0 }
        : undefined,
    [descriptor.x, descriptor.y]
  );

  switch (descriptor.descriptor_type) {
    case "markdown":
      return descriptor.content ? (
        <CollapsibleWidgetWrapper
          descriptor={descriptor}
          onDismiss={onDismiss}
          onDragEnd={onDragEnd}
          onToggleCollapse={onToggleCollapse}
          isExpanded={isExpanded}
        >
          <MarkdownWidget
            content={descriptor.content}
            onDismiss={onDismiss}
            dragPosition={dragPosition}
            onDragEnd={onDragEnd}
          />
        </CollapsibleWidgetWrapper>
      ) : null;
    case "card":
      return (
        <CollapsibleWidgetWrapper
          descriptor={descriptor}
          onDismiss={onDismiss}
          onDragEnd={onDragEnd}
          onToggleCollapse={onToggleCollapse}
          isExpanded={isExpanded}
        >
          <CardWidget
            title={descriptor.title || ""}
            content={descriptor.content || ""}
            actions={[]}
            onDismiss={onDismiss}
            dragPosition={dragPosition}
            onDragEnd={onDragEnd}
          />
        </CollapsibleWidgetWrapper>
      );
    case "form":
      return (
        <CollapsibleWidgetWrapper
          descriptor={descriptor}
          onDismiss={onDismiss}
          onDragEnd={onDragEnd}
          onToggleCollapse={onToggleCollapse}
          isExpanded={isExpanded}
        >
          <FormWidget
            title={descriptor.title}
            fields={descriptor.fields || []}
            submitLabel={descriptor.submit_button_text}
            onSubmit={NOOP_FN}
            onDismiss={onDismiss}
            dragPosition={dragPosition}
            onDragEnd={onDragEnd}
          />
        </CollapsibleWidgetWrapper>
      );
    case "progress":
      return (
        <CollapsibleWidgetWrapper
          descriptor={descriptor}
          onDismiss={onDismiss}
          onDragEnd={onDragEnd}
          onToggleCollapse={onToggleCollapse}
          isExpanded={isExpanded}
        >
          <ProgressWidget
            title={descriptor.title || "Processing"}
            value={(descriptor.progress_percent || 0) / 100}
            statusText={descriptor.status_text}
            onDismiss={onDismiss}
            dragPosition={dragPosition}
            onDragEnd={onDragEnd}
          />
        </CollapsibleWidgetWrapper>
      );
    case "action":
      return (
        <CollapsibleWidgetWrapper
          descriptor={descriptor}
          onDismiss={onDismiss}
          onDragEnd={onDragEnd}
          onToggleCollapse={onToggleCollapse}
          isExpanded={isExpanded}
        >
          <ActionWidget
            title={descriptor.title}
            content={descriptor.content}
            buttonText={descriptor.button_text || "Action"}
            onAction={NOOP_FN}
            onDismiss={onDismiss}
            dragPosition={dragPosition}
            onDragEnd={onDragEnd}
          />
        </CollapsibleWidgetWrapper>
      );
    case "confirmation":
      return (
        <CollapsibleWidgetWrapper
          descriptor={descriptor}
          onDismiss={onDismiss}
          onDragEnd={onDragEnd}
          onToggleCollapse={onToggleCollapse}
          isExpanded={isExpanded}
        >
          <ConfirmationWidget
            title={descriptor.title || "Confirm"}
            message={descriptor.message || ""}
            confirmLabel={descriptor.confirm_label}
            cancelLabel={descriptor.cancel_label}
            onConfirm={NOOP_FN}
            onCancel={NOOP_FN}
            onDismiss={onDismiss}
            dragPosition={dragPosition}
            onDragEnd={onDragEnd}
          />
        </CollapsibleWidgetWrapper>
      );
    case "image":
      return (
        <CollapsibleWidgetWrapper
          descriptor={descriptor}
          onDismiss={onDismiss}
          onDragEnd={onDragEnd}
          onToggleCollapse={onToggleCollapse}
          isExpanded={isExpanded}
        >
          <ImageWidget
            title={descriptor.title}
            content={descriptor.content}
            caption={descriptor.content}
            onDismiss={onDismiss}
            dragPosition={dragPosition}
            onDragEnd={onDragEnd}
          />
        </CollapsibleWidgetWrapper>
      );
    case "gallery":
      return (
        <CollapsibleWidgetWrapper
          descriptor={descriptor}
          onDismiss={onDismiss}
          onDragEnd={onDragEnd}
          onToggleCollapse={onToggleCollapse}
          isExpanded={isExpanded}
        >
          <GalleryWidget
            title={descriptor.title}
            content={descriptor.content}
            onDismiss={onDismiss}
            dragPosition={dragPosition}
            onDragEnd={onDragEnd}
          />
        </CollapsibleWidgetWrapper>
      );
    case "chart":
      return (
        <CollapsibleWidgetWrapper
          descriptor={descriptor}
          onDismiss={onDismiss}
          onDragEnd={onDragEnd}
          onToggleCollapse={onToggleCollapse}
          isExpanded={isExpanded}
        >
          <ChartWidget
            title={descriptor.title}
            content={descriptor.content}
            chartType={(descriptor.metadata?.chart_type as "bar" | "line" | "pie" | "area") || "bar"}
            data={descriptor.metadata?.data as Array<Record<string, string | number>>}
            dataKeys={descriptor.metadata?.data_keys as string[]}
            onDismiss={onDismiss}
            dragPosition={dragPosition}
            onDragEnd={onDragEnd}
          />
        </CollapsibleWidgetWrapper>
      );
    default:
      return null;
  }
});

export default function HomePage() {
  const [view, setView] = useState<View>("main");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [widgets, setWidgets] = useState<UIDescriptor[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [connectors, setConnectors] = useState<Record<string, boolean>>({
    searxng: false,
    mem0: false,
    qdrant: false,
  });
  const [health, setHealth] = useState<string>("unknown");

  // Island UI state - 3-state cycle system
  type WidgetState = "island" | "card" | "full";
  const [islandPositions, setIslandPositions] = useState<Record<string, { x: number; y: number }>>({});
  const [widgetStates, setWidgetStates] = useState<Record<string, WidgetState>>({});

  // NEW: Track if widgets have started arriving (for auto-hiding progress)
  const [hasWidgetsArrived, setHasWidgetsArrived] = useState(false);

  // Use ref for drag state to prevent handler recreation (for click vs drag detection)
  const dragStateRef = useRef<Record<string, {
    startPos: { x: number; y: number };
    hasMoved: boolean;
    moveDistance: number;
  }>>({});

  // Cache for widget handlers to prevent re-renders (FIXED)
  const handlersCacheRef = useRef<Record<string, {
    onDismiss: () => void;
    onDragStart: (_: any, info: PanInfo) => void;
    onDrag: (_: any, info: PanInfo) => void;
    onDragEnd: (_: any, info: PanInfo) => void;
    onDragEndCompat: (x: number, y: number) => void;
    onClick: (e: React.MouseEvent) => void;
    onToggleCollapse: () => void;
  }>>({});

  // Threshold for click vs drag (in pixels)
  const CLICK_THRESHOLD = 5;

  // WebSocket connection state
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);

  // QA progress state
  type QACheckpointStatus = "running" | "passed" | "failed";
  type QACheckpoint = {
    status: QACheckpointStatus;
    checkpoint: string;
    details: Record<string, unknown>;
  };

  const [qaProgress, setQaProgress] = useState<Record<string, QACheckpoint>>({});

  // Update QA checkpoint
  const updateQACheckpoint = useCallback((checkpoint: string, status: QACheckpointStatus, details: Record<string, unknown> = {}) => {
    setQaProgress(prev => ({
      ...prev,
      [checkpoint]: { status, checkpoint, details }
    }));
    console.log(`✓ QA ${checkpoint}: ${status}`);
  }, []);

  // Reset QA progress
  const resetQAProgress = useCallback(() => {
    setQaProgress({});
    setWidgetStates({});
    setHasWidgetsArrived(false); // Reset widget arrival flag
  }, []);

  // Handle incoming widget message
  const handleWidgetMessage = useCallback((data: { id: string; type: string; title?: string; content?: string; metadata?: Record<string, unknown> }) => {
    const widgetId = data.id || `widget-${Date.now()}`;
    const widget: UIDescriptor = {
      descriptor_id: widgetId,
      descriptor_type: data.type as any,
      title: data.title,
      content: data.content,
      metadata: data.metadata,
      dismissible: true,
    };

    setWidgets(prev => {
      // Append new widgets at the end to prevent re-rendering existing ones
      return [...prev, widget];
    });
    setHasWidgetsArrived(true); // Mark that widgets have arrived
    console.log(`📦 Widget delivered: ${widget.descriptor_type}`);

    // 3-state cycle: new widgets start in "island" state (default)
    // Users click to cycle: island -> card -> full -> island
  }, []);

  // Complete message handler
  const [generationComplete, setGenerationComplete] = useState(false);

  const handleCompleteMessage = useCallback((data: Record<string, unknown>) => {
    console.log("🎯 Generation complete:", data);
    setGenerationComplete(true);
    setLoading(false);
  }, []);

  // Message router - dispatches to appropriate handler
  const setupWebSocketHandlers = useCallback((ws: WebSocket) => {
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case "qa_progress":
            updateQACheckpoint(data.data.checkpoint, data.data.status as QACheckpointStatus, data.data.details);
            break;

          case "widget":
            handleWidgetMessage(data.data);
            break;

          case "complete":
            handleCompleteMessage(data.data);
            ws.close();
            break;

          case "error":
            console.error("🔴 Error:", data.message);
            setLoading(false);
            ws.close();
            break;

          default:
            console.warn("Unknown message type:", data);
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
      }
    };
  }, [updateQACheckpoint, handleWidgetMessage, handleCompleteMessage]);

  // Feature flag for island UI
  const enableIslands = process.env.NEXT_PUBLIC_ENABLE_ISLANDS === "true";

  // Assign initial positions to new widgets (two-side layout, respecting UI boundaries)
  useEffect(() => {
    if (!enableIslands) return;

    const positionedWidgetIds = new Set(Object.keys(islandPositions));
    const newWidgets = widgets.filter((w) => !positionedWidgetIds.has(w.descriptor_id));
    if (newWidgets.length === 0) return;

    // Get safe spawn zones that respect UI boundaries
    const safeZones = getSafeSpawnZone(sidebarOpen);

    const viewportHeight = typeof window !== "undefined" ? window.innerHeight : 800;
    const centerY = viewportHeight / 2;

    const MIN_SPACING = 100;

    const newPositions: Record<string, { x: number; y: number }> = {};
    const existingPositions = Object.values(islandPositions);

    newWidgets.forEach((widget, index) => {
      // Alternate between left and right zones
      const zone = index % 2 === 0 ? "left" : "right";
      const zoneConfig = safeZones[zone];

      const minXVal = zoneConfig.minX;
      const maxXVal = zoneConfig.maxX;
      const minYVal = zoneConfig.minY;
      const maxYVal = zoneConfig.maxY;

      // Try to find non-overlapping position in chosen zone
      for (let attempt = 0; attempt < 15; attempt++) {
        const randomX = Math.random() * (maxXVal - minXVal) + minXVal;
        const randomY = Math.random() * (maxYVal - minYVal) + minYVal;

        const hasCollision = existingPositions.some((pos) => {
          const dx = pos.x - randomX;
          const dy = pos.y - randomY;
          return Math.sqrt(dx * dx + dy * dy) < MIN_SPACING;
        });

        if (!hasCollision) {
          newPositions[widget.descriptor_id] = { x: randomX, y: randomY };
          existingPositions.push({ x: randomX, y: randomY });
          return;
        }
      }

      // Fallback - place in center of zone
      newPositions[widget.descriptor_id] = {
        x: (minXVal + maxXVal) / 2,
        y: Math.min(maxYVal, Math.max(minYVal, centerY + (Math.random() - 0.5) * 200)),
      };
      existingPositions.push(newPositions[widget.descriptor_id]);
    });

    setIslandPositions((prev) => ({ ...prev, ...newPositions }));
  }, [widgets, enableIslands, sidebarOpen]);

  // Fetch health status
  useEffect(() => {
    fetch(`${apiUrl}/api/v1/health`)
      .then((res) => res.json())
      .then((data) => setHealth(data.status))
      .catch(() => setHealth("disconnected"));
  }, [apiUrl]);

  // Fetch sessions
  useEffect(() => {
    fetch(`${apiUrl}/api/v1/mock/sessions`)
      .then((res) => res.json())
      .then((data) => setSessions(data.sessions || []))
      .catch(() => setSessions([]));
  }, [apiUrl]);

  const generateContent = async (prompt: string, widgetType?: string) => {
    if (!prompt.trim()) return;

    console.log("🟢 generateContent called:", { prompt, widgetType });
    setLoading(true);
    try {
      console.log("🟢 Fetching from:", `${apiUrl}/api/v1/generate-widget`);
      const res = await fetch(`${apiUrl}/api/v1/generate-widget`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          widget_type: widgetType,
        }),
      });

      console.log("🟢 Response status:", res.status, res.statusText);
      const data = await res.json();
      console.log("🟢 Response data:", data);
      console.log("🟢 data.widgets:", data.widgets);
      console.log("🟢 data.widgets length:", data.widgets?.length);

      // API now returns { widgets: [...], tools_used: [...], reasoning: "..." }
      // Map each widget from backend response to frontend format
      const newWidgets: UIDescriptor[] = (data.widgets || []).map((w: any) => {
        console.log("🟢 Mapping widget:", w);
        return {
          descriptor_id: w.id,
          descriptor_type: w.type,
          title: w.title,
          content: w.content,
          dismissible: w.dismissible ?? true,
          ...(w.metadata && { metadata: w.metadata }),
          ...(w.metadata?.fields && { fields: w.metadata.fields }),
          ...(w.metadata?.submit_label && { submit_button_text: w.metadata.submit_label }),
          ...(w.metadata?.status_text && { status_text: w.metadata.status_text }),
          ...(w.metadata?.value !== undefined && { progress_percent: w.metadata.value * 100 }),
          ...(w.metadata?.button_text && { button_text: w.metadata.button_text }),
          ...(w.metadata?.action_id && { action_id: w.metadata.action_id }),
          ...(w.metadata?.confirm_label && { confirm_label: w.metadata.confirm_label }),
          ...(w.metadata?.cancel_label && { cancel_label: w.metadata.cancel_label }),
        };
      });

      // Add all new widgets to the state (ReAct may have generated multiple)
      console.log("🟢 Adding widgets to state:", newWidgets);
      setWidgets((prev) => {
        const updated = [...newWidgets, ...prev];
        console.log("🟢 Updated widgets state:", updated);
        console.log("🟢 Total widgets after update:", updated.length);
        return updated;
      });

      if (data.reasoning) {
        console.log("🟢 ReAct reasoning:", data.reasoning);
      }
      if (data.tools_used) {
        console.log("🟢 Tools used:", data.tools_used);
      }
    } catch (error) {
      console.error("🔴 Failed to generate content:", error);
    }
    setLoading(false);
  };

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket(`${apiUrl.replace("http", "ws")}/api/v1/ws/generate-widget`);

    ws.onopen = () => {
      console.log("🔌 WebSocket connected");
      setWsConnection(ws);
    };

    ws.onerror = (error) => {
      console.error("🔴 WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("🔌 WebSocket closed");
      setWsConnection(null);
    };

    return ws;
  }, [apiUrl]);

  // Main generation function using WebSocket
  const generateContentWithWebSocket = useCallback(async (prompt: string) => {
    if (!prompt.trim()) return;

    setLoading(true);
    resetQAProgress();
    setGenerationComplete(false);

    const ws = connectWebSocket();
    setupWebSocketHandlers(ws);

    // Send query once connected
    ws.onopen = () => {
      console.log("🔌 WebSocket connected, sending query");
      ws.send(JSON.stringify({
        query: prompt,
        device_context: "desktop",
      }));
    };
  }, [connectWebSocket, resetQAProgress, setupWebSocketHandlers]);

  const handleSendMessage = useCallback((message: string) => {
    generateContentWithWebSocket(message);
  }, [generateContentWithWebSocket]);

  // Handle voice toggle (not implemented yet)
  const handleVoiceToggle = useCallback(() => {
    console.log("Voice toggle requested (not implemented)");
  }, []);

  // Dismiss widget - memoized to prevent re-renders, uses startTransition for batching
  const dismissWidget = useCallback((id: string) => {
    console.log(`🗑️ [DISMISS] Widget ${id} being dismissed`);
    // Use startTransition to batch all state updates as lower-priority
    startTransition(() => {
      setWidgets((prev) => {
        const filtered = prev.filter((w) => w.descriptor_id !== id);
        console.log(`🗑️ [DISMISS] Widgets before: ${prev.length}, after: ${filtered.length}`);
        return filtered;
      });
      setIslandPositions((prev) => {
        const updated = { ...prev };
        delete updated[id];
        return updated;
      });
      setWidgetStates((prev) => {
        const updated = { ...prev };
        delete updated[id];
        return updated;
      });
    });
    // Clean up cached handlers (sync, not part of transition)
    if (handlersCacheRef.current[id]) {
      delete handlersCacheRef.current[id];
    }
  }, []);

  // Toggle widget collapse - memoized to prevent re-renders
  const toggleWidgetCollapse = useCallback((id: string) => {
    setWidgets((prev) =>
      prev.map((w) =>
        w.descriptor_id === id ? { ...w, collapsed: !w.collapsed } : w
      )
    );
  }, []);

  // Handle drag end - MUST be before getWidgetHandlers (which depends on this)
  // x, y are OFFSETS from the current position (not absolute positions)
  const handleIslandDragEnd = useCallback((id: string, x: number, y: number) => {
    console.log(`🖱️ [DRAG END] ${id} → offset x: ${x.toFixed(1)}, y: ${y.toFixed(1)}`);
    console.trace("Drag end call stack:");

    setIslandPositions((prev) => {
      const currentPos = prev[id] || { x: window.innerWidth / 2, y: window.innerHeight / 2 };
      const newX = currentPos.x + x;
      const newY = currentPos.y + y;

      // Boundary checking - keep widget on screen (island diameter: 56px)
      const islandDiameter = 56;
      const padding = 20;
      const boundedX = Math.max(padding, Math.min(window.innerWidth - islandDiameter - padding, newX));
      const boundedY = Math.max(padding, Math.min(window.innerHeight - islandDiameter - padding, newY));

      const updated = { ...prev, [id]: { x: boundedX, y: boundedY } };
      console.log(`🖱️ [DRAG END] ${id}: (${currentPos.x.toFixed(1)}, ${currentPos.y.toFixed(1)}) + (${x.toFixed(1)}, ${y.toFixed(1)}) → (${boundedX.toFixed(1)}, ${boundedY.toFixed(1)})`);
      console.log(`🖱️ [DRAG END] Updated island positions, total: ${Object.keys(updated).length}`);
      return updated;
    });

    setWidgets((prev) => {
      const currentWidget = prev.find((w) => w.descriptor_id === id);
      const currentX = currentWidget?.x ?? window.innerWidth / 2;
      const currentY = currentWidget?.y ?? window.innerHeight / 2;
      const newX = currentX + x;
      const newY = currentY + y;

      // Boundary checking - keep widget on screen
      const islandDiameter = 56;
      const padding = 20;
      const boundedX = Math.max(padding, Math.min(window.innerWidth - islandDiameter - padding, newX));
      const boundedY = Math.max(padding, Math.min(window.innerHeight - islandDiameter - padding, newY));

      const updated = prev.map((w) =>
        w.descriptor_id === id ? { ...w, x: boundedX, y: boundedY } : w
      );
      console.log(`🖱️ [DRAG END] Updated widget ${id} x/y in widgets array`);
      return updated;
    });
  }, []);

  // Create stable handlers for each widget - FIXED: Use cache to prevent re-renders
  const getWidgetHandlers = useCallback((id: string) => {
    // Return cached handlers if available
    if (handlersCacheRef.current[id]) {
      return handlersCacheRef.current[id];
    }

    // Create new handlers and cache them
    const handleDragStart = (_: any, info: PanInfo) => {
      dragStateRef.current[id] = {
        startPos: { x: info.point.x, y: info.point.y },
        hasMoved: false,
        moveDistance: 0,
      };
    };

    const handleDrag = (_: any, info: PanInfo) => {
      const state = dragStateRef.current[id];
      if (!state) return;
      const distance = Math.hypot(
        info.point.x - state.startPos.x,
        info.point.y - state.startPos.y
      );
      dragStateRef.current[id] = { ...state, hasMoved: distance > CLICK_THRESHOLD, moveDistance: distance };
    };

    const handleDragEnd = (_: any, info: PanInfo) => {
      const state = dragStateRef.current[id];
      const isClick = state && state.moveDistance < CLICK_THRESHOLD;

      if (!isClick) {
        handleIslandDragEnd(id, info.offset.x, info.offset.y);
      }

      delete dragStateRef.current[id];
    };

    const onDragEndCompat = (x: number, y: number) => {
      const state = dragStateRef.current[id];
      const isClick = state && state.moveDistance < CLICK_THRESHOLD;

      if (!isClick) {
        handleIslandDragEnd(id, x, y);
      }

      delete dragStateRef.current[id];
    };

    const handlers = {
      onDismiss: () => dismissWidget(id),
      onDragStart: handleDragStart,
      onDrag: handleDrag,
      onDragEnd: handleDragEnd,
      onDragEndCompat,
      onClick: (e: React.MouseEvent) => {
        const state = dragStateRef.current[id];
        const isClick = !state || state.moveDistance < CLICK_THRESHOLD;
        if (isClick) {
          toggleWidgetCollapse(id);
        }
      },
      onToggleCollapse: () => toggleWidgetCollapse(id),
    };

    // Cache the handlers
    handlersCacheRef.current[id] = handlers;
    return handlers;
  }, [dismissWidget, handleIslandDragEnd, toggleWidgetCollapse, CLICK_THRESHOLD]);

  // 3-State Cycle: island -> card -> full -> island
  const cycleWidgetState = useCallback((id: string) => {
    console.log(`🔄 [CYCLE] Widget ${id} state change requested`);
    console.trace("Cycle call stack:");
    setWidgetStates(prev => {
      const currentState = prev[id] || "island";
      const nextState: Record<WidgetState, WidgetState> = {
        island: "card",
        card: "full",
        full: "island"
      };
      console.log(`🔄 [CYCLE] ${id}: ${currentState} -> ${nextState[currentState]}`);
      return { ...prev, [id]: nextState[currentState] };
    });
  }, []);

  const handlePanelClose = useCallback((id: string) => {
    setWidgetStates(prev => ({ ...prev, [id]: "island" }));
  }, []);

  const handleMobileBubbleExpand = useCallback((id: string) => {
    setWidgetStates(prev => ({ ...prev, [id]: "full" }));
  }, []);

  // Memoized stable handlers for Widget3StateRenderer to prevent re-renders
  const stableHandlers = useMemo(() => {
    const cache: Record<string, {
      onCycleState: () => void;
      onDragEnd: (x: number, y: number) => void;
      onDismiss: () => void;
      onPanelClose: () => void;
    }> = {};

    widgets.forEach(w => {
      const id = w.descriptor_id;
      cache[id] = {
        onCycleState: () => cycleWidgetState(id),
        onDragEnd: (x: number, y: number) => handleIslandDragEnd(id, x, y),
        onDismiss: () => dismissWidget(id),
        onPanelClose: () => handlePanelClose(id),
      };
    });

    return cache;
  }, [widgets, cycleWidgetState, handleIslandDragEnd, dismissWidget, handlePanelClose]);

  // Sidebar navigation handlers - memoized to prevent re-renders
  const handleCloseSidebar = useCallback(() => setSidebarOpen(false), []);
  const handleToggleSidebar = useCallback(() => setSidebarOpen(prev => !prev), []);
  const handleNavMain = useCallback(() => { setView("main"); setSidebarOpen(false); }, []);
  const handleNavGallery = useCallback(() => { setView("gallery"); setSidebarOpen(false); }, []);
  const handleNavSessions = useCallback(() => { setView("sessions"); setSidebarOpen(false); }, []);
  const handleNavConnectors = useCallback(() => { setView("connectors"); setSidebarOpen(false); }, []);

  // Sidebar
  const Sidebar = () => (
    <motion.aside
      initial={{ x: -320 }}
      animate={{ x: sidebarOpen ? 0 : -320 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="fixed left-0 top-0 h-full w-80 bg-card border-r border-border z-40 flex flex-col"
    >
      <div className="p-4 border-b border-border flex items-center justify-between">
        <h2 className="font-semibold text-lg">Navigation</h2>
        <Button variant="ghost" size="icon" onClick={handleCloseSidebar}>
          <X className="w-5 h-5" />
        </Button>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        <Button
          variant={view === "main" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={handleNavMain}
        >
          <MessageSquare className="w-4 h-4 mr-2" />
          Main Workspace
        </Button>
        <Button
          variant={view === "gallery" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={handleNavGallery}
        >
          <Images className="w-4 h-4 mr-2" />
          Widget Gallery
        </Button>
        <Button
          variant={view === "sessions" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={handleNavSessions}
        >
          <History className="w-4 h-4 mr-2" />
          Sessions
        </Button>
        <Button
          variant={view === "connectors" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={handleNavConnectors}
        >
          <Database className="w-4 h-4 mr-2" />
          Connectors
        </Button>
      </nav>

      <div className="p-4 border-t border-border">
        <ThemeToggle />
      </div>
    </motion.aside>
  );

  // Main view
  const MainView = () => (
    <div className="space-y-6 relative">
      {/* Mobile Bubble Layer - visible only on mobile */}
      {enableIslands && (
        <MobileBubbleLayer
          widgets={widgets}
          expandedIds={new Set(Object.keys(widgetStates).filter(id => widgetStates[id] === "full"))}
          onExpand={handleMobileBubbleExpand}
          onDismiss={dismissWidget}
        />
      )}

      {/* Generated Widgets - 3-State Cycle System (Island -> Card -> Full) */}
      <LayoutGroup>
        <AnimatePresence mode="popLayout">
          {widgets.map((widget, index) => {
          const handlers = getWidgetHandlers(widget.descriptor_id);

          // Island UI mode - 3-state cycle system
          if (enableIslands) {
            const viewportWidth = typeof window !== "undefined" ? window.innerWidth : 1200;
            const viewportHeight = typeof window !== "undefined" ? window.innerHeight : 800;
            const centerX = viewportWidth / 2;
            const centerY = viewportHeight / 2;

            // Get current state (defaults to island)
            const currentState = widgetStates[widget.descriptor_id] || "island";
            const position = islandPositions[widget.descriptor_id] || { x: centerX, y: centerY };
            const baseZIndex = 1000 + index;

            // Use stable handlers to prevent re-renders
            const widgetHandlers = stableHandlers[widget.descriptor_id];
            return (
              <Widget3StateRenderer
                key={widget.descriptor_id}
                widget={widget}
                state={currentState}
                position={position}
                zIndex={baseZIndex}
                onCycleState={widgetHandlers?.onCycleState || handlers.onDismiss}
                onDragEnd={widgetHandlers?.onDragEnd || handlers.onDragEndCompat}
                onDismiss={widgetHandlers?.onDismiss || handlers.onDismiss}
              />
            );
          }

          // Traditional mode (CollapsibleWidgetWrapper) - use controlled isExpanded
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

      {widgets.length === 0 && (
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

  // Gallery view
  const GalleryView = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Widget Gallery</CardTitle>
          <CardDescription>
            All 10 generative UI widget types showcased with example content
          </CardDescription>
        </CardHeader>
      </Card>

      <MarkdownWidget
        content={`# Markdown Heading

This is a **markdown block** widget that supports:

- **Bold** and *italic* text
- Lists (ordered and unordered)
- [Links](https://example.com)
- \`inline code\` and code blocks

\`\`\`javascript
const greeting = "Hello, World!";
console.log(greeting);
\`\`\`

> Blockquotes are also supported

This widget is perfect for displaying AI-generated explanations, documentation, and formatted text.
        `}
      />

      <CardWidget
        title="Travel Tips: Japan"
        content="### Best Time to Visit\n\nSpring (March-May) for cherry blossoms or Autumn (November) for fall colors.\n\n### Must-Visit Places\n- Tokyo (modern culture)\n- Kyoto (temples and traditions)\n- Osaka (food capital)\n\n### Travel Tips\n- Get a JR Pass for unlimited train travel\n- Learn basic Japanese phrases\n- Cash is still king in many places"
        actions={[
          { label: "View Details", action: "view-details" },
          { label: "Book Now", action: "book-now" },
        ]}
      />

      <FormWidget
        title="User Feedback Form"
        fields={[
          { name: "name", type: "text", label: "Your Name" },
          { name: "email", type: "email", label: "Email Address" },
          { name: "feedback", type: "textarea", label: "Your Feedback" },
          { name: "rating", type: "select", label: "Rating", options: ["Excellent", "Good", "Fair", "Poor"] },
        ]}
        submitLabel="Submit Feedback"
        onSubmit={NOOP_FN}
      />

      <ProgressWidget
        title="Processing Documents"
        value={0.65}
        statusText="15 of 23 documents processed"
      />

      <ActionWidget
        title="Start Analysis"
        content="Click to begin processing your data"
        buttonText="Start New Analysis"
        onAction={NOOP_FN}
      />

      <ConfirmationWidget
        title="Delete Document"
        message="Are you sure you want to delete this document? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        variant="destructive"
        onConfirm={NOOP_FN}
        onCancel={NOOP_FN}
      />

      <ImageWidget
        title="Mountain Landscape"
        content="A beautiful mountain landscape showcasing nature's grandeur"
        caption="Photo from Picsum Photos"
      />

      <GalleryWidget
        title="Nature Collection"
        content="A curated gallery of stunning nature photographs"
      />

      <ChartWidget
        title="Monthly Sales Data"
        content="Revenue trends over the past 6 months showing consistent growth"
        chartType="bar"
      />
    </div>
  );

  // Sessions view
  const SessionsView = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Sessions</CardTitle>
          <CardDescription>
            Your previous conversation sessions and generated widgets
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">No sessions yet</p>
          ) : (
            <div className="space-y-2">
              {sessions.map((session) => (
                <div
                  key={session.id || session.session_id}
                  className="p-3 border rounded-lg hover:bg-muted cursor-pointer"
                >
                  <h3 className="font-medium">{session.title}</h3>
                  <p className="text-sm text-muted-foreground">
                    {session.created_at || session.date || "Unknown date"}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );

  // Memoized connector toggle handlers to prevent re-renders in map
  const connectorToggleHandlers = useMemo(() => {
    const handlers: Record<string, () => void> = {};
    Object.keys(connectors).forEach(name => {
      handlers[name] = () => setConnectors(prev => ({ ...prev, [name]: !prev[name as keyof typeof prev] }));
    });
    return handlers;
  }, [connectors]);

  // Connectors view
  const ConnectorsView = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Connectors</CardTitle>
          <CardDescription>
            Configure external service connections
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(connectors).map(([name, connected]) => (
            <div key={name} className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <h3 className="font-medium capitalize">{name}</h3>
                <p className="text-sm text-muted-foreground capitalize">
                  {connected ? "Connected" : "Not connected"}
                </p>
              </div>
              <Button
                variant={connected ? "outline" : "default"}
                onClick={connectorToggleHandlers[name]}
              >
                {connected ? "Disconnect" : "Connect"}
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <Sidebar />

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 h-16 border-b border-border bg-card/80 backdrop-blur-sm z-30 flex items-center px-4 lg:px-6">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleToggleSidebar}
          className="mr-4"
        >
          <Plus className="w-5 h-5" />
        </Button>
        <h1 className="text-xl font-semibold">{appName}</h1>
        <div className="ml-auto flex items-center gap-2">
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm ${
            health === "healthy" ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100" :
            health === "disconnected" ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100" :
            "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100"
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              health === "healthy" ? "bg-green-500" :
              health === "disconnected" ? "bg-red-500" :
              "bg-gray-500"
            }`} />
            {health === "healthy" ? "Connected" : health}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-20 px-4 lg:px-6 pb-32">
        {view === "main" && <MainView />}
        {view === "gallery" && <GalleryView />}
        {view === "sessions" && <SessionsView />}
        {view === "connectors" && <ConnectorsView />}
      </main>

      {/* Central Island - always visible at bottom center */}
      {/* FIXED: Auto-hide QA progress when widgets arrive */}
      {!hasWidgetsArrived && <QAProgressDisplay checkpoints={qaProgress} />}
      <CentralIsland
        onSendMessage={handleSendMessage}
        onVoiceToggle={handleVoiceToggle}
      />

      {/* Mobile expanded panel */}
      {enableIslands && Object.values(widgetStates).filter(s => s === "full").length > 0 && (
        <div className="md:hidden fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          {widgets
            .filter((w) => widgetStates[w.descriptor_id] === "full")
            .map((widget) => {
              const handlers = getWidgetHandlers(widget.descriptor_id);
              const widgetHandlers = stableHandlers[widget.descriptor_id];
              const dragPos = { x: widget.x || 0, y: widget.y || 0 };
              return (
                <div key={widget.descriptor_id} className="w-full max-w-md max-h-[80vh] overflow-auto">
                  <DirectWidgetRenderer
                    descriptor={widget}
                    onDismiss={handlers.onDismiss}
                    dragPosition={dragPos}
                    onDragEnd={handlers.onDragEndCompat}
                  />
                  <Button
                    variant="outline"
                    className="w-full mt-4"
                    onClick={widgetHandlers?.onPanelClose}
                  >
                    Close
                  </Button>
                </div>
              );
            })}
        </div>
      )}
    </div>
  );
}
