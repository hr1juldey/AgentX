"use client";

import { useState, useEffect, useCallback, useMemo, memo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, MessageSquare, X, Sparkles, Images, History, Database } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ThemeToggle } from "@/components/showcase/theme-toggle";
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

type View = "main" | "gallery" | "sessions" | "connectors";

// Widget content renderer without wrapper (for Island mode)
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
          onSubmit={() => {}}
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
          onAction={() => {}}
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
          onConfirm={() => {}}
          onCancel={() => {}}
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
        />
      );
    case "gallery":
      return (
        <GalleryWidget
          title={descriptor.title}
          content={descriptor.content}
          onDismiss={onDismiss}
          dragPosition={dragPosition}
          onDragEnd={onDragEnd}
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
    default:
      return null;
  }
});

// Collapsible wrapper for widgets - shows mini island when collapsed (Traditional mode only)
const CollapsibleWidgetWrapper = memo(function CollapsibleWidgetWrapper({
  descriptor,
  onDismiss,
  onDragEnd,
  onToggleCollapse,
  children,
}: {
  descriptor: UIDescriptor;
  onDismiss: () => void;
  onDragEnd: (x: number, y: number) => void;
  onToggleCollapse: () => void;
  children: React.ReactNode;
}) {
  const [isCollapsed, setIsCollapsed] = useState(descriptor.collapsed || false);

  // Sync with descriptor state
  useEffect(() => {
    setIsCollapsed(descriptor.collapsed || false);
  }, [descriptor.collapsed]);

  const handleToggle = useCallback(() => {
    const newState = !isCollapsed;
    setIsCollapsed(newState);
    onToggleCollapse();
  }, [isCollapsed, onToggleCollapse]);

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
      default: return "📦";
    }
  }, [descriptor.descriptor_type]);

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
        {isCollapsed ? (
          <motion.div
            key="collapsed"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="relative"
          >
            <motion.div
              drag
              dragElastic={0.2}
              dragMomentum={false}
              dragConstraints={{ left: -500, right: 500, top: -500, bottom: 500 }}
              whileDrag={{ scale: 1.05, cursor: "grabbing", zIndex: 50 }}
              onDragEnd={(_, info) => onDragEnd(
                (descriptor.x || 0) + info.offset.x,
                (descriptor.y || 0) + info.offset.y
              )}
              style={{ x: descriptor.x || 0, y: descriptor.y || 0 }}
              className="relative bg-card border border-border rounded-full cursor-grab shadow-lg hover:shadow-xl px-4 py-2 flex items-center gap-2"
            >
              <span className="text-lg">{getWidgetIcon()}</span>
              <span className="text-sm font-medium truncate max-w-[120px]">
                {descriptor.title || descriptor.descriptor_type}
              </span>
              {/* Expand button */}
              <button
                onClick={handleToggle}
                className="ml-1 p-1 rounded-full hover:bg-muted transition-colors"
                aria-label="Expand"
              >
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {/* Dismiss button */}
              {onDismiss && (
                <button
                  onClick={onDismiss}
                  className="p-1 rounded-full hover:bg-destructive/10 hover:text-destructive transition-colors"
                  aria-label="Dismiss"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </motion.div>
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
}: {
  descriptor: UIDescriptor;
  onDismiss: () => void;
  onDragEnd: (x: number, y: number) => void;
  onToggleCollapse: () => void;
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
        >
          <FormWidget
            title={descriptor.title}
            fields={descriptor.fields || []}
            submitLabel={descriptor.submit_button_text}
            onSubmit={() => {}}
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
        >
          <ActionWidget
            title={descriptor.title}
            content={descriptor.content}
            buttonText={descriptor.button_text || "Action"}
            onAction={() => {}}
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
        >
          <ConfirmationWidget
            title={descriptor.title || "Confirm"}
            message={descriptor.message || ""}
            confirmLabel={descriptor.confirm_label}
            cancelLabel={descriptor.cancel_label}
            onConfirm={() => {}}
            onCancel={() => {}}
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

  // Island UI state
  const [islandPositions, setIslandPositions] = useState<Record<string, { x: number; y: number }>>({});
  // Support multiple expanded widgets at once - use Set<string>
  const [expandedPanelIds, setExpandedPanelIds] = useState<Set<string>>(new Set());

  // Feature flag for island UI
  const enableIslands = process.env.NEXT_PUBLIC_ENABLE_ISLANDS === "true";

  // Assign initial positions to new widgets (stack along right edge)
  useEffect(() => {
    if (!enableIslands) return;

    // Only track widget IDs, not the entire islandPositions object
    const positionedWidgetIds = new Set(Object.keys(islandPositions));
    const newWidgets = widgets.filter((w) => !positionedWidgetIds.has(w.descriptor_id));
    if (newWidgets.length === 0) return;

    const viewportWidth = typeof window !== "undefined" ? window.innerWidth : 1200;
    const edgeMargin = 80;
    const spacing = 70;
    const startY = 100;

    const newPositions: Record<string, { x: number; y: number }> = {};
    const existingCount = positionedWidgetIds.size;

    newWidgets.forEach((widget, index) => {
      newPositions[widget.descriptor_id] = {
        x: viewportWidth - edgeMargin,
        y: startY + (existingCount + index) * spacing,
      };
    });

    setIslandPositions((prev) => ({ ...prev, ...newPositions }));
  }, [widgets, enableIslands]);

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
          widget_type: widgetType,  // Optional - DSPy ReAct selects if not provided
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
          // Preserve the full metadata object for chart widgets
          ...(w.metadata && { metadata: w.metadata }),
          // Extract individual metadata fields for other widgets
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

      // Log reasoning if available (for debugging)
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

  // Handle send message from CentralIsland
  const handleSendMessage = useCallback((message: string) => {
    generateContent(message);
  }, []);

  // Handle voice toggle (not implemented yet)
  const handleVoiceToggle = useCallback(() => {
    console.log("Voice toggle requested (not implemented)");
  }, []);

  // Dismiss widget - memoized to prevent re-renders
  const dismissWidget = useCallback((id: string) => {
    setWidgets((prev) => prev.filter((w) => w.descriptor_id !== id));
    // Also remove from island positions
    setIslandPositions((prev) => {
      const updated = { ...prev };
      delete updated[id];
      return updated;
    });
    // Also close expanded panel if this was the one
    setExpandedPanelIds((prev) => {
      const newSet = new Set(prev);
      newSet.delete(id);
      return newSet;
    });
  }, []);

  // Update widget position after drag - memoized to prevent re-renders
  const updateWidgetPosition = useCallback((id: string, x: number, y: number) => {
    // Update widget descriptor x/y (for expanded widgets)
    setWidgets((prev) =>
      prev.map((w) =>
        w.descriptor_id === id ? { ...w, x, y } : w
      )
    );

    // Also update island positions state (for island buttons)
    setIslandPositions((prev) => ({
      ...prev,
      [id]: { x, y },
    }));
  }, []);

  // Toggle widget collapse - memoized to prevent re-renders
  const toggleWidgetCollapse = useCallback((id: string) => {
    setWidgets((prev) =>
      prev.map((w) =>
        w.descriptor_id === id ? { ...w, collapsed: !w.collapsed } : w
      )
    );
  }, []);

  // Create stable handlers for each widget - memoized to prevent re-renders
  const createWidgetHandlers = useCallback((id: string) => ({
    onDismiss: () => dismissWidget(id),
    onDragEnd: (x: number, y: number) => updateWidgetPosition(id, x, y),
    onToggleCollapse: () => toggleWidgetCollapse(id),
  }), [dismissWidget, updateWidgetPosition, toggleWidgetCollapse]);

  // Island UI handlers - support multiple open widgets (max 6)
  const MAX_EXPANDED_WIDGETS = 6;
  const handleIslandClick = useCallback((id: string) => {
    setExpandedPanelIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id); // Collapse (toggle off)
      } else if (newSet.size < MAX_EXPANDED_WIDGETS) {
        newSet.add(id); // Expand (allows multiple, max 6)
      } else {
        console.warn(`Maximum ${MAX_EXPANDED_WIDGETS} widgets can be expanded at once`);
      }
      return newSet;
    });
  }, []);

  const handleIslandDragEnd = useCallback((id: string, x: number, y: number) => {
    // Update island positions state (for island buttons)
    setIslandPositions((prev) => ({
      ...prev,
      [id]: { x, y },
    }));

    // Also update widget descriptor x/y (for expanded widgets)
    setWidgets((prev) =>
      prev.map((w) =>
        w.descriptor_id === id ? { ...w, x, y } : w
      )
    );
  }, []);

  const handlePanelClose = useCallback((id: string) => {
    setExpandedPanelIds((prev) => {
      const newSet = new Set(prev);
      newSet.delete(id);
      return newSet;
    });
  }, []);

  const handleMobileBubbleExpand = useCallback((id: string) => {
    setExpandedPanelIds((prev) => {
      const newSet = new Set(prev);
      newSet.add(id);
      return newSet;
    });
  }, []);

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
        <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(false)}>
          <X className="w-5 h-5" />
        </Button>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        <Button
          variant={view === "main" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => { setView("main"); setSidebarOpen(false); }}
        >
          <MessageSquare className="w-4 h-4 mr-2" />
          Main Workspace
        </Button>
        <Button
          variant={view === "gallery" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => { setView("gallery"); setSidebarOpen(false); }}
        >
          <Images className="w-4 h-4 mr-2" />
          Widget Gallery
        </Button>
        <Button
          variant={view === "sessions" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => { setView("sessions"); setSidebarOpen(false); }}
        >
          <History className="w-4 h-4 mr-2" />
          Sessions
        </Button>
        <Button
          variant={view === "connectors" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => { setView("connectors"); setSidebarOpen(false); }}
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
          expandedIds={expandedPanelIds}
          onExpand={handleMobileBubbleExpand}
          onDismiss={dismissWidget}
        />
      )}

      {/* Generated Widgets - Island UI or Traditional Layout */}
      <AnimatePresence mode="popLayout">
        {widgets.map((widget, index) => {
          const handlers = createWidgetHandlers(widget.descriptor_id);

          // Island UI mode - Use ToolIsland + DirectWidgetRenderer (no wrapper)
          if (enableIslands) {
            // FORCE CENTER OF SCREEN - always visible
            const viewportWidth = typeof window !== "undefined" ? window.innerWidth : 1200;
            const viewportHeight = typeof window !== "undefined" ? window.innerHeight : 800;
            const centerX = viewportWidth / 2;
            const centerY = viewportHeight / 2;

            // Stack islands in center with offset
            const offset = (index - (widgets.length - 1) / 2) * 80;
            const position = islandPositions[widget.descriptor_id] || { x: centerX + offset, y: centerY };
            const isExpanded = expandedPanelIds.has(widget.descriptor_id);

            const dragPos = { x: widget.x || position.x, y: widget.y || position.y };

            return (
              <div key={widget.descriptor_id} style={{ position: "fixed", zIndex: 1000 + index }}>
                {/* Only show island button when NOT expanded */}
                {!isExpanded && (
                  <ToolIsland
                    widget={widget}
                    position={position}
                    isActive={isExpanded}
                    onClick={() => handleIslandClick(widget.descriptor_id)}
                    onDragEnd={(x, y) => handleIslandDragEnd(widget.descriptor_id, x, y)}
                    onDismiss={handlers.onDismiss}
                  />
                )}

                {/* Expanded state - render widget WITH collapse button */}
                {isExpanded && (
                  <div className="relative">
                    {/* Collapse button in top-left corner */}
                    <button
                      onClick={() => handleIslandClick(widget.descriptor_id)}
                      className="absolute top-0 left-0 z-10 p-2 m-2 rounded-full bg-primary text-primary-foreground shadow-lg hover:shadow-xl transition-all hover:scale-110"
                      aria-label="Collapse widget"
                      title="Collapse to island"
                    >
                      <MessageSquare className="w-4 h-4" />
                    </button>
                    <DirectWidgetRenderer
                      descriptor={widget}
                      onDismiss={handlers.onDismiss}
                      dragPosition={dragPos}
                      onDragEnd={handlers.onDragEnd}
                    />
                  </div>
                )}
              </div>
            );
          }

          // Traditional mode (CollapsibleWidgetWrapper)
          return (
            <WidgetRenderer
              key={widget.descriptor_id}
              descriptor={widget}
              onDismiss={handlers.onDismiss}
              onDragEnd={handlers.onDragEnd}
              onToggleCollapse={handlers.onToggleCollapse}
            />
          );
        })}
      </AnimatePresence>

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
        onSubmit={() => {}}
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
        onAction={() => {}}
      />

      <ConfirmationWidget
        title="Delete Document"
        message="Are you sure you want to delete this document? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        variant="destructive"
        onConfirm={() => {}}
        onCancel={() => {}}
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
                onClick={() => setConnectors((prev) => ({ ...prev, [name]: !prev[name as keyof typeof prev] }))}
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
      <header className="fixed top-0 left-0 right-0 h-16 border-b border-border bg-card z-30 flex items-center px-4 lg:px-6">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSidebarOpen(!sidebarOpen)}
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
      <CentralIsland
        onSendMessage={handleSendMessage}
        onVoiceToggle={handleVoiceToggle}
      />

      {/* Mobile expanded panel */}
      {enableIslands && expandedPanelIds.size > 0 && (
        <div className="md:hidden fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          {widgets
            .filter((w) => expandedPanelIds.has(w.descriptor_id))
            .map((widget) => {
              const handlers = createWidgetHandlers(widget.descriptor_id);
              const dragPos = { x: widget.x || 0, y: widget.y || 0 };
              return (
                <div key={widget.descriptor_id} className="w-full max-w-md max-h-[80vh] overflow-auto">
                  <DirectWidgetRenderer
                    descriptor={widget}
                    onDismiss={handlers.onDismiss}
                    dragPosition={dragPos}
                    onDragEnd={handlers.onDragEnd}
                  />
                  <Button
                    variant="outline"
                    className="w-full mt-4"
                    onClick={() => handlePanelClose(widget.descriptor_id)}
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
