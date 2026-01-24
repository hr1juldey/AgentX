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
import { IsolatedWidget } from "@/components/widgets/isolated-widget";
import { ToolIsland, MobileBubbleLayer } from "@/components/islands";
import { useWidgetStore, useUIStore, useNetworkStore } from "@/store";

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

type View = "main" | "gallery" | "sessions" | "connectors";

// ============================================================================
// NOTE: Widget3StateRenderer removed - replaced by IsolatedWidget
// which implements the State Colocation Pattern for better performance
// ============================================================================

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
  // ============================================================================
  // PHASE 1 MIGRATION: Using Zustand stores for global state
  // ============================================================================
  // UI Store (navigation, sidebar, loading)
  const currentView = useUIStore((s) => s.currentView);
  const sidebarOpen = useUIStore((s) => s.sidebarOpen);
  const globalLoading = useUIStore((s) => s.globalLoading);
  const setCurrentView = useUIStore((s) => s.setCurrentView);
  const setSidebarOpen = useUIStore((s) => s.setSidebarOpen);
  const setGlobalLoading = useUIStore((s) => s.setGlobalLoading);

  // Network Store (sessions, connectors, health, WebSocket, QA progress)
  const sessions = useNetworkStore((s) => s.sessions);
  const connectors = useNetworkStore((s) => s.connectors);
  const apiHealth = useNetworkStore((s) => s.apiHealth);
  const wsConnection = useNetworkStore((s) => s.wsConnection);
  const qaProgress = useNetworkStore((s) => s.qaProgress);
  const setSessions = useNetworkStore((s) => s.setSessions);
  const setConnector = useNetworkStore((s) => s.setConnector);
  const setApiHealth = useNetworkStore((s) => s.setApiHealth);
  const setWsConnection = useNetworkStore((s) => s.setWsConnection);
  const setQaProgress = useNetworkStore((s) => s.setQaProgress);
  const resetQaProgress = useNetworkStore((s) => s.resetQaProgress);

  // ============================================================================
  // LOCAL STATE: Keep transient UI state as useState
  // ============================================================================
  // Loading state (using local name for compatibility with existing code)
  const loading = globalLoading;
  const setLoading = (isLoading: boolean) => setGlobalLoading(isLoading);

  // Health state (using local name for compatibility with existing code)
  const health = apiHealth;
  const setHealth = (newHealth: string) => setApiHealth(newHealth as 'unknown' | 'healthy' | 'unhealthy' | 'disconnected');

  // Local widgets array (for non-island mode and MobileBubbleLayer)
  const [widgets, setWidgets] = useState<UIDescriptor[]>([]);

  // ============================================================================
  // REMOVED: Centralized widget state (widgetStates, islandPositions)
  // Now handled by IsolatedWidget with State Colocation Pattern
  // ============================================================================

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

  // ============================================================================
  // QA PROGRESS: Now using Network Store
  // ============================================================================
  type QACheckpointStatus = "running" | "passed" | "failed";

  // Update QA checkpoint - now uses store action
  const updateQACheckpoint = useCallback((checkpoint: string, status: QACheckpointStatus, details: Record<string, unknown> = {}) => {
    setQaProgress(checkpoint, status, details);
    console.log(`✓ QA ${checkpoint}: ${status}`);
  }, [setQaProgress]);

  // Reset QA progress - now uses store action
  const handleResetQAProgress = useCallback(() => {
    resetQaProgress();
    // Note: widgetStates removed - IsolatedWidget handles its own state
    setHasWidgetsArrived(false); // Reset widget arrival flag
  }, [resetQaProgress]);

  // ============================================================================
  // STATE COLOCATION PATTERN: New simple stable callbacks for IsolatedWidget
  // These have empty deps = never recreated, preventing cascade re-renders
  // ============================================================================

  /**
   * Simple stable callback for widget deletion - now uses Zustand store
   * Empty deps = stable forever, prevents re-renders of other widgets
   */
  const handleWidgetDelete = useCallback((id: string) => {
    startTransition(() => {
      // Remove from Zustand store
      useWidgetStore.getState().removeWidget(id);
      // Also remove from local widgets array (for non-island mode and MobileBubbleLayer)
      setWidgets(prev => prev.filter(w => w.descriptor_id !== id));
    });
  }, []); // ← Empty deps = stable forever

  /**
   * Safe position generator - deterministic positioning for new widgets
   * Uses hash of widget ID for consistent positioning
   * Respects UI boundaries (header: 56px, sidebar: 320px when open)
   * Note: This is now handled by Zustand store, but kept for MobileBubbleLayer
   */
  const generateSafePosition = useCallback((id: string, existingWidgets: UIDescriptor[] = []) => {
    const vw = typeof window !== "undefined" ? window.innerWidth : 1200;
    const vh = typeof window !== "undefined" ? window.innerHeight : 800;

    // Safe zones (respect header: 56px, sidebar: 320px when open)
    const sidebarOffset = sidebarOpen ? 320 : 0;
    const minX = sidebarOffset + 80;
    const maxX = vw - 80;
    const minY = 80;
    const maxY = vh - 200;

    // Widget collision dimensions (approximate)
    const widgetWidth = 300;  // Approximate widget width
    const widgetHeight = 200; // Approximate widget height
    const padding = 20;       // Padding between widgets

    // Use hash of ID for deterministic starting position
    const hash = id.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);

    // Try up to 50 positions to find a non-colliding spot
    for (let attempt = 0; attempt < 50; attempt++) {
      // Generate position with hash + attempt offset for determinism
      const x = ((hash + attempt * 137) % (maxX - minX - widgetWidth)) + minX;
      const y = ((hash + attempt * 251) % (maxY - minY - widgetHeight)) + minY;

      // Check for collisions with existing widgets
      let hasCollision = false;
      for (const widget of existingWidgets) {
        const wx = widget.x ?? (maxX / 2);
        const wy = widget.y ?? (maxY / 2);

        // Simple AABB collision detection
        const xOverlap = Math.abs(x - wx) < (widgetWidth + padding);
        const yOverlap = Math.abs(y - wy) < (widgetHeight + padding);

        if (xOverlap && yOverlap) {
          hasCollision = true;
          break;
        }
      }

      // Return first non-colliding position
      if (!hasCollision) {
        return { x, y };
      }
    }

    // Fallback: use hash-based position (may overlap but guaranteed to return)
    const x = (hash % (maxX - minX)) + minX;
    const y = (hash % (maxY - minY)) + minY;
    return { x, y };
  }, [sidebarOpen]);

  // Handle incoming widget message - now uses Zustand store
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

    // Add to Zustand store (handles position generation and state initialization)
    useWidgetStore.getState().addWidget(widget, { sidebarOpen });

    // Also keep local widgets array in sync (for non-island mode and MobileBubbleLayer)
    setWidgets(prev => [...prev, widget]);

    setHasWidgetsArrived(true); // Mark that widgets have arrived
    console.log(`📦 Widget delivered: ${widget.descriptor_type}`);

    // Note: View state management is now handled by Zustand store
    // New widgets start in "island" state (default)
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

  // Pre-compute safe positions for all widgets with collision detection
  // NOTE: For island mode with Zustand, positions are handled by the store
  // This is only used for non-island mode and MobileBubbleLayer
  const widgetPositions = useMemo(() => {
    const positions: Record<string, { x: number; y: number }> = {};
    const placed: UIDescriptor[] = [];

    for (const widget of widgets) {
      // Use widget's initial x/y if available (from creation, NOT from drag updates)
      if (widget.x !== undefined && widget.y !== undefined) {
        positions[widget.descriptor_id] = { x: widget.x, y: widget.y };
        placed.push({ ...widget, x: widget.x, y: widget.y });
        continue;
      }

      // Generate NEW position for widgets without x/y (newly spawned)
      const pos = generateSafePosition(widget.descriptor_id, placed);
      positions[widget.descriptor_id] = pos;
      placed.push({ ...widget, x: pos.x, y: pos.y });
    }

    return positions;
  }, [widgets, generateSafePosition]);

  // Get widget IDs from Zustand store for island mode rendering
  // NOTE: We use useMemo to compute IDs from the widgets Map to avoid infinite re-renders
  // (accessing s.widgets directly gives us a stable Map reference)
  const storeWidgets = useWidgetStore((s) => s.widgets);
  const storeWidgetIds = useMemo(() => Array.from(storeWidgets.keys()), [storeWidgets]);

  // Feature flag for island UI
  const enableIslands = process.env.NEXT_PUBLIC_ENABLE_ISLANDS === "true";

  // ============================================================================
  // REMOVED: Old position assignment useEffect
  // IsolatedWidget now uses generateSafePosition() for deterministic positioning
  // ============================================================================

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
    handleResetQAProgress();
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
  }, [connectWebSocket, handleResetQAProgress, setupWebSocketHandlers]);

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
      // NOTE: islandPositions and widgetStates removed - IsolatedWidget handles its own state
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
  // NOTE: Simplified - islandPositions removed, only updates widgets array for traditional mode
  const handleIslandDragEnd = useCallback((id: string, x: number, y: number) => {
    console.log(`🖱️ [DRAG END] ${id} → offset x: ${x.toFixed(1)}, y: ${y.toFixed(1)}`);
    console.trace("Drag end call stack:");

    // NOTE: setIslandPositions removed - IsolatedWidget handles its own position state

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

  // ============================================================================
  // REMOVED: Old island mode handlers (cycleWidgetState, handlePanelClose,
  // handleMobileBubbleExpand, stableHandlers)
  // Now handled by IsolatedWidget with State Colocation Pattern
  // ============================================================================

  // Sidebar navigation handlers - memoized to prevent re-renders
  const handleCloseSidebar = useCallback(() => setSidebarOpen(false), [setSidebarOpen]);
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const handleToggleSidebar = useCallback(() => toggleSidebar(), [toggleSidebar]);
  const handleNavMain = useCallback(() => { setCurrentView("main"); setSidebarOpen(false); }, [setCurrentView, setSidebarOpen]);
  const handleNavGallery = useCallback(() => { setCurrentView("gallery"); setSidebarOpen(false); }, [setCurrentView, setSidebarOpen]);
  const handleNavSessions = useCallback(() => { setCurrentView("sessions"); setSidebarOpen(false); }, [setCurrentView, setSidebarOpen]);
  const handleNavConnectors = useCallback(() => { setCurrentView("connectors"); setSidebarOpen(false); }, [setCurrentView, setSidebarOpen]);

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
          variant={currentView === "main" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={handleNavMain}
        >
          <MessageSquare className="w-4 h-4 mr-2" />
          Main Workspace
        </Button>
        <Button
          variant={currentView === "gallery" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={handleNavGallery}
        >
          <Images className="w-4 h-4 mr-2" />
          Widget Gallery
        </Button>
        <Button
          variant={currentView === "sessions" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={handleNavSessions}
        >
          <History className="w-4 h-4 mr-2" />
          Sessions
        </Button>
        <Button
          variant={currentView === "connectors" ? "secondary" : "ghost"}
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
      {/* NOTE: With State Colocation, widgets track their own state.
          MobileBubbleLayer simplified - parent no longer tracks widget states. */}
      {enableIslands && (
        <MobileBubbleLayer
          widgets={widgets}
          expandedIds={new Set<string>()} // Empty - widgets track their own state
          onExpand={() => {}} // No-op - widgets track their own state
          onDismiss={handleWidgetDelete}
        />
      )}

      {/* Generated Widgets - 3-State Cycle System (Island -> Card -> Full) */}
      <LayoutGroup>
        <AnimatePresence mode="popLayout">
          {enableIslands ? (
            // Island UI mode - use Zustand store with IsolatedWidget
            storeWidgetIds.map((id) => (
              <IsolatedWidget
                key={id}
                descriptorId={id}
              />
            ))
          ) : (
            // Traditional mode (CollapsibleWidgetWrapper) - use controlled isExpanded
            widgets.map((widget) => {
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
            })
          )}
        </AnimatePresence>
      </LayoutGroup>

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
      handlers[name] = () => setConnector(name as keyof typeof connectors, !connectors[name as keyof typeof connectors]);
    });
    return handlers;
  }, [connectors, setConnector]);

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
        {currentView === "main" && <MainView />}
        {currentView === "gallery" && <GalleryView />}
        {currentView === "sessions" && <SessionsView />}
        {currentView === "connectors" && <ConnectorsView />}
      </main>

      {/* Central Island - always visible at bottom center */}
      {/* FIXED: Auto-hide QA progress when widgets arrive */}
      {!hasWidgetsArrived && <QAProgressDisplay checkpoints={qaProgress} />}
      <CentralIsland
        onSendMessage={handleSendMessage}
        onVoiceToggle={handleVoiceToggle}
      />

      {/* ============================================================================
          REMOVED: Mobile expanded panel (relied on widgetStates, stableHandlers)
          With State Colocation, IsolatedWidget handles its own "full" state display
          ============================================================================ */}
    </div>
  );
}
