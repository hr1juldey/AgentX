"use client";

import { useState, useEffect, useCallback, useMemo, memo, useRef, startTransition } from "react";
import { motion, AnimatePresence, PanInfo, LayoutGroup } from "framer-motion";
import { Plus, MessageSquare, X, Sparkles, Images, History, Database, ChevronDown, Minimize2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ThemeToggle } from "@/components/showcase/theme-toggle";
import { QAProgressDisplay } from "@/components/ui/qa-progress";
import { CentralIsland } from "@/components/ui/central-island";
import { IsolatedWidget } from "@/components/widgets/isolated-widget";
import { DirectWidgetRenderer } from "@/components/widgets/direct-widget-renderer";
import { CollapsibleWidgetWrapper } from "@/components/widgets/collapsible-widget-wrapper";
import { WidgetRenderer } from "@/components/widgets/widget-renderer";
import { ToolIsland, MobileBubbleLayer, IslandModeWidgets } from "@/components/islands";
import { Sidebar } from "@/components/home/sidebar";
import { SessionsView, ConnectorsView } from "@/components/home/views";
import { GalleryView } from "@/components/home/gallery-view";
import { MainView } from "@/components/home/main-view";
import { PageHeader } from "@/components/home/page-header";
import { useNavigation } from "@/hooks/use-navigation";
import { useContentGeneration } from "@/hooks/use-content-generation";
import { useWebSocketGeneration } from "@/hooks/use-websocket-generation";
import { useWidgetHandlers } from "@/hooks/use-widget-handlers";
import { useWidgetStore, useUIStore, useNetworkStore } from "@/store";
import type { UIDescriptor, Session, View, QACheckpointStatus } from "@/types/widget-types";
import { API_CONFIG, INTERACTION_CONFIG } from "@/constants/widget-constants";
import { generateSafePosition } from "@/services/position-service";

// EXTRACTED: UIDescriptor interface (was lines 30-79)
// EXTRACTED: Session interface (was lines 81-87)
// EXTRACTED: View type (was line 97)
// See: /types/widget-types.ts

// EXTRACTED: API_CONFIG.URL, API_CONFIG.APP_NAME constants (was lines 89-90)
// See: /constants/widget-constants.ts

// Stable no-op functions to prevent re-renders (identity-stable across renders)
const NOOP_FN = () => {};
const NOOP_DRAG_FN = (_x: number, _y: number) => {};
const STOP_PROPAGATION = (e: React.MouseEvent) => e.stopPropagation();

// ============================================================================
// NOTE: Widget3StateRenderer removed - replaced by IsolatedWidget
// which implements the State Colocation Pattern for better performance
// ============================================================================

// EXTRACTED: DirectWidgetRenderer (was lines 51-221)
// See: /components/widgets/direct-widget-renderer.tsx

// EXTRACTED: IslandModeWidgets (was lines 44-83)
// See: /components/islands/island-mode-widgets.tsx

// EXTRACTED: CollapsibleWidgetWrapper (was lines 83-187)
// See: /components/widgets/collapsible-widget-wrapper.tsx

// EXTRACTED: WidgetRenderer (was lines 51-90)
// See: /components/widgets/widget-renderer.tsx

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

  // EXTRACTED: Content generation logic
  // See: /hooks/use-content-generation.ts
  const { generateContent } = useContentGeneration({
    setLoading,
    setWidgets,
  });

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
  // EXTRACTED: INTERACTION_CONFIG.CLICK_THRESHOLD constant (was line 636)
  // Defined as constant outside component to prevent handler recreation
  // See: /constants/widget-constants.ts
  // eslint-disable-next-line react-hooks/exhaustive-deps

  // Stable empty Set for MobileBubbleLayer to prevent re-renders
  // Using ref ensures same object reference across renders
  const emptyExpandedIdsRef = useRef<Set<string>>(new Set());
  const stableEmptyExpandFnRef = useRef<() => void>(() => {});

  // ============================================================================
  // QA PROGRESS: Now using Network Store
  // ============================================================================
  // EXTRACTED: QACheckpointStatus type to /types/widget-types.ts

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

      // CRITICAL: Only update local state when NOT in island mode
      // Island mode derives everything from Zustand store - no duplication!
      // enableIslands is a build-time constant from env var
      const enableIslands = process.env.NEXT_PUBLIC_ENABLE_ISLANDS === "true";
      if (!enableIslands) {
        setWidgets(prev => prev.filter(w => w.descriptor_id !== id));
      }
    });
  }, []); // ← Empty deps = stable forever (enableIslands is a constant)

  /**
   * Safe position generator - deterministic positioning for new widgets
   * Uses hash of widget ID for consistent positioning
   * Respects UI boundaries (header: 56px, sidebar: 320px when open)
   * Note: This is now handled by Zustand store, but kept for MobileBubbleLayer
   *
   * EXTRACTED: generateSafePosition logic (was lines 639-690)
   * See: /services/position-service.ts
   */
  const generateSafePositionCallback = useCallback((id: string, existingWidgets: UIDescriptor[] = []) => {
    return generateSafePosition(id, existingWidgets, { sidebarOpen });
  }, [sidebarOpen]);

  // Handle incoming widget message - now uses Zustand store
  const handleWidgetMessage = useCallback((data: unknown) => {
    const widgetData = data as { id: string; type: string; title?: string; content?: string; metadata?: Record<string, unknown> };
    const widgetId = widgetData.id || `widget-${Date.now()}`;
    const widget: UIDescriptor = {
      descriptor_id: widgetId,
      descriptor_type: widgetData.type as any,
      title: widgetData.title,
      content: widgetData.content,
      metadata: widgetData.metadata,
      dismissible: true,
    };

    // Add to Zustand store (handles position generation and state initialization)
    useWidgetStore.getState().addWidget(widget, { sidebarOpen });

    // CRITICAL: Only update local state when NOT in island mode
    // Island mode derives everything from Zustand store - no duplication!
    // This prevents cascade re-renders caused by dual state management
    // enableIslands is a build-time constant from env var
    const enableIslands = process.env.NEXT_PUBLIC_ENABLE_ISLANDS === "true";
    if (!enableIslands) {
      setWidgets(prev => [...prev, widget]);
    }

    setHasWidgetsArrived(true); // Mark that widgets have arrived
    console.log(`📦 Widget delivered: ${widget.descriptor_type}`);

    // Note: View state management is now handled by Zustand store
    // New widgets start in "island" state (default)
    // Users click to cycle: island -> card -> full -> island
  }, [sidebarOpen]); // enableIslands is a constant, excluded from deps

  // Complete message handler
  const [generationComplete, setGenerationComplete] = useState(false);

  const handleCompleteMessage = useCallback((data: unknown) => {
    console.log("🎯 Generation complete:", data);
    setGenerationComplete(true);
    setLoading(false);
  }, []);

  // EXTRACTED: WebSocket generation logic
  // See: /hooks/use-websocket-generation.ts
  const { setupWebSocketHandlers, connectWebSocket, generateContentWithWebSocket } = useWebSocketGeneration({
    updateQACheckpoint,
    handleWidgetMessage,
    handleCompleteMessage,
    setLoading,
    setWsConnection,
    handleResetQAProgress,
    setGenerationComplete,
  });

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
      const pos = generateSafePositionCallback(widget.descriptor_id, placed);
      positions[widget.descriptor_id] = pos;
      placed.push({ ...widget, x: pos.x, y: pos.y });
    }

    return positions;
  }, [widgets, generateSafePositionCallback]);

  // Get widget IDs from Zustand store for island mode rendering
  // With atomic state pattern, we use the widgetIds array directly
  // This array only changes when widgets are added/removed, not when individual widget data changes
  const storeWidgetIds = useWidgetStore((s) => s.widgetIds);

  // DIAGNOSTIC: Track parent (HomePage) renders
  const prevStoreWidgetIdsRef = useRef<string[] | undefined>(undefined);
  const parentRenderCountRef = useRef(0);

  useEffect(() => {
    parentRenderCountRef.current += 1;
    const idsChanged = prevStoreWidgetIdsRef.current?.join(',') !== storeWidgetIds.join(',');

    console.log(`[HomePage] Render #${parentRenderCountRef.current}`, {
      widgetCount: storeWidgetIds.length,
      idsChanged,
      widgetIds: storeWidgetIds,
    });

    prevStoreWidgetIdsRef.current = storeWidgetIds;
  });

  // Feature flag for island UI
  const enableIslands = process.env.NEXT_PUBLIC_ENABLE_ISLANDS === "true";

  // ============================================================================
  // REMOVED: Old position assignment useEffect
  // IsolatedWidget now uses generateSafePosition() for deterministic positioning
  // ============================================================================

  // Fetch health status
  useEffect(() => {
    fetch(`${API_CONFIG.URL}/api/v1/health`)
      .then((res) => res.json())
      .then((data) => setHealth(data.status))
      .catch(() => setHealth("disconnected"));
  }, [API_CONFIG.URL]);

  // Fetch sessions
  useEffect(() => {
    fetch(`${API_CONFIG.URL}/api/v1/mock/sessions`)
      .then((res) => res.json())
      .then((data) => setSessions(data.sessions || []))
      .catch(() => setSessions([]));
  }, [API_CONFIG.URL]);

  // EXTRACTED: generateContent (was lines 343-406)
  // See: /hooks/use-content-generation.ts

  // EXTRACTED: connectWebSocket, generateContentWithWebSocket (was lines 324-364)
  // See: /hooks/use-websocket-generation.ts

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

  // EXTRACTED: Widget handlers (toggleWidgetCollapse, handleIslandDragEnd, getWidgetHandlers)
  // See: /hooks/use-widget-handlers.ts
  const { toggleWidgetCollapse, handleIslandDragEnd, getWidgetHandlers } = useWidgetHandlers({
    dismissWidget,
    setWidgets,
    dragStateRef,
    handlersCacheRef,
  });

  // ============================================================================
  // REMOVED: Old island mode handlers (cycleWidgetState, handlePanelClose,
  // handleMobileBubbleExpand, stableHandlers)
  // Now handled by IsolatedWidget with State Colocation Pattern
  // ============================================================================

  // EXTRACTED: Navigation handlers (was lines 585-592)
  // See: /hooks/use-navigation.ts
  const navigation = useNavigation();
  const {
    handleCloseSidebar,
    handleToggleSidebar,
    handleNavMain,
    handleNavGallery,
    handleNavSessions,
    handleNavConnectors,
  } = navigation;

  // Sidebar component reference (uses handlers defined above)
  // EXTRACTED: Sidebar (was lines 664-717)
  // See: /components/home/sidebar.tsx

  // EXTRACTED: MainView (was lines 596-660)
  // See: /components/home/main-view.tsx

  // EXTRACTED: galleryDescriptors, GalleryView (was lines 698-816)
  // See: /components/home/gallery-view.tsx

  // EXTRACTED: SessionsView (was lines 856-886)
  // See: /components/home/views.tsx

  // EXTRACTED: connectorToggleHandlers, ConnectorsView (was lines 888-927)
  // ConnectorsView now handles toggle internally via onToggleConnector prop
  // See: /components/home/views.tsx

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        currentView={currentView}
        onCloseSidebar={handleCloseSidebar}
        onNavMain={handleNavMain}
        onNavGallery={handleNavGallery}
        onNavSessions={handleNavSessions}
        onNavConnectors={handleNavConnectors}
      />

      {/* Header */}
      <PageHeader
        health={health}
        onToggleSidebar={handleToggleSidebar}
      />

      {/* Main Content */}
      <main className="pt-20 px-4 lg:px-6 pb-32">
        {currentView === "main" && (
          <MainView
            enableIslands={enableIslands}
            emptyExpandedIds={emptyExpandedIdsRef}
            stableEmptyExpandFn={stableEmptyExpandFnRef}
            onWidgetDelete={handleWidgetDelete}
            storeWidgetIds={storeWidgetIds}
            widgets={widgets}
            getWidgetHandlers={getWidgetHandlers}
          />
        )}
        {currentView === "gallery" && <GalleryView />}
        {currentView === "sessions" && <SessionsView sessions={sessions} />}
        {currentView === "connectors" && (
          <ConnectorsView
            connectors={connectors}
            onToggleConnector={(name) => setConnector(name as keyof typeof connectors, !connectors[name as keyof typeof connectors])}
          />
        )}
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
