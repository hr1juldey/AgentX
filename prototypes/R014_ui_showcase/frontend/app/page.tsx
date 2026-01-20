"use client";

import { useState, useEffect, useCallback, useMemo, memo, useRef } from "react";
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

// Memoized widget renderer to prevent re-renders of other widgets
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

// Collapsible wrapper for widgets - shows mini island when collapsed
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
  const [isCollapsed, setIsCollapsed] = useState(descriptor.collapsed || false)

  // Sync with descriptor state
  useEffect(() => {
    setIsCollapsed(descriptor.collapsed || false)
  }, [descriptor.collapsed])

  const handleToggle = useCallback(() => {
    const newState = !isCollapsed
    setIsCollapsed(newState)
    onToggleCollapse()
  }, [isCollapsed, onToggleCollapse])

  // Widget type icons
  const getWidgetIcon = useCallback(() => {
    switch (descriptor.descriptor_type) {
      case "markdown": return "📝"
      case "card": return "📇"
      case "form": return "📋"
      case "progress": return "📊"
      case "action": return "⚡"
      case "confirmation": return "❓"
      case "image": return "🖼️"
      case "gallery": return "🖼️"
      case "chart": return "📈"
      default: return "📦"
    }
  }, [descriptor.descriptor_type])

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
            {/* Collapse button - absolute positioned */}
            <div className="relative">
              <button
                onClick={handleToggle}
                className="absolute -top-3 left-1/2 -translate-x-1/2 z-10 p-1 rounded-full bg-card border border-border shadow-md hover:bg-muted transition-all"
                aria-label="Collapse"
              >
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
              </button>
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
});

export default function HomePage() {
  const [view, setView] = useState<View>("main");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [inputPrompt, setInputPrompt] = useState("");
  const [widgets, setWidgets] = useState<UIDescriptor[]>([]);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<string>("checking...");
  const [sessions, setSessions] = useState<Session[]>([]);

  // Fetch health status
  useEffect(() => {
    fetch(`${apiUrl}/health`)
      .then((res) => res.json())
      .then((data) => setHealth(data.status))
      .catch(() => setHealth("disconnected"));
  }, [apiUrl]);

  // Fetch sessions
  useEffect(() => {
    fetch(`${apiUrl}/api/v1/mock/sessions`)
      .then((res) => res.json())
      .then((data) => setSessions(data || []))
      .catch(() => setSessions([]));
  }, [apiUrl]);

  // Generate content - uses DSPy ReAct agent for auto widget selection
  // Can now generate multiple widgets based on user query
  const generateContent = async (prompt: string, widgetType?: string) => {
    if (!prompt.trim()) return;

    setLoading(true);
    try {
      // Use /generate-widget endpoint with DSPy ReAct agent for auto selection
      const res = await fetch(`${apiUrl}/api/v1/generate-widget`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          widget_type: widgetType,  // Optional - DSPy ReAct selects if not provided
        }),
      });
      const data = await res.json();

      // API now returns { widgets: [...], tools_used: [...], reasoning: "..." }
      // Map each widget from backend response to frontend format
      const newWidgets: UIDescriptor[] = (data.widgets || []).map((w: any) => ({
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
      }));

      // Add all new widgets to the state (ReAct may have generated multiple)
      setWidgets((prev) => [...newWidgets, ...prev]);
      setInputPrompt(""); // Clear input after successful generation

      // Log reasoning if available (for debugging)
      if (data.reasoning) {
        console.log("ReAct reasoning:", data.reasoning);
      }
      if (data.tools_used) {
        console.log("Tools used:", data.tools_used);
      }
    } catch (error) {
      console.error("Failed to generate content:", error);
    }
    setLoading(false);
  };

  // Dismiss widget - memoized to prevent re-renders
  const dismissWidget = useCallback((id: string) => {
    setWidgets((prev) => prev.filter((w) => w.descriptor_id !== id));
  }, []);

  // Update widget position after drag - memoized to prevent re-renders
  const updateWidgetPosition = useCallback((id: string, x: number, y: number) => {
    setWidgets((prev) =>
      prev.map((w) =>
        w.descriptor_id === id ? { ...w, x, y } : w
      )
    );
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
          <Sparkles className="w-4 h-4 mr-2" />
          Main Showcase
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
          Past Sessions
        </Button>
        <Button
          variant={view === "connectors" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => { setView("connectors"); setSidebarOpen(false); }}
        >
          <Database className="w-4 h-4 mr-2" />
          Data Connectors
        </Button>
      </nav>

      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>Backend:</span>
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            health === "healthy" ? "bg-green-500/20 text-green-500" : "bg-red-500/20 text-red-500"
          }`}>
            {health}
          </span>
        </div>
      </div>
    </motion.aside>
  );

  // Main view
  const MainView = () => (
    <div className="space-y-6">
      {/* Welcome Card */}
      <Card className="bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            {appName}
          </CardTitle>
          <CardDescription>
            Generative UI showcase with DSPy + Ollama content hydration
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Click the Central Island button below to open the chat interface.
            Describe what you want to see, and the AI will create an appropriate widget.
          </p>
        </CardContent>
      </Card>

      {/* Generated Widgets - Simple layout without Voronoi */}
      <AnimatePresence mode="popLayout">
        {widgets.map((widget) => {
          const handlers = createWidgetHandlers(widget.descriptor_id);
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
          <CardTitle>Past Sessions</CardTitle>
          <CardDescription>
            Review your previous conversations and generated widgets
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {sessions.map((session) => (
              <div
                key={session.session_id || session.id}
                className="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">{session.title}</h3>
                  <span className="text-xs text-muted-foreground">
                    {new Date(session.created_at || session.date || "").toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
            {sessions.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-8">
                No past sessions found. Start generating content to create a session.
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  // Connectors view
  const ConnectorsView = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Data Connectors</CardTitle>
          <CardDescription>
            System integration status and configuration
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h3 className="font-medium">Ollama LLM</h3>
                <p className="text-sm text-muted-foreground">Local inference engine</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                health === "healthy" ? "bg-green-500/20 text-green-500" : "bg-red-500/20 text-red-500"
              }`}>
                {health === "healthy" ? "Connected" : "Disconnected"}
              </span>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h3 className="font-medium">DSPy Framework</h3>
                <p className="text-sm text-muted-foreground">Programmatic LLM interactions</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                health === "healthy" ? "bg-green-500/20 text-green-500" : "bg-red-500/20 text-red-500"
              }`}>
                {health === "healthy" ? "Active" : "Inactive"}
              </span>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h3 className="font-medium">FastAPI Backend</h3>
                <p className="text-sm text-muted-foreground">REST API server</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                health === "healthy" ? "bg-green-500/20 text-green-500" : "bg-red-500/20 text-red-500"
              }`}>
                {health === "healthy" ? "Running" : "Stopped"}
              </span>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h3 className="font-medium">Next.js Frontend</h3>
                <p className="text-sm text-muted-foreground">BFF (Backend For Frontend)</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-500">
                Active
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Overlay for sidebar */}
      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <Sidebar />

      {/* Header */}
      <header className="border-b border-border sticky top-0 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 z-20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(true)}
              >
                <MessageSquare className="w-5 h-5" />
              </Button>
              <h1 className="text-xl font-bold">{appName}</h1>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {view === "main" && <MainView />}
        {view === "gallery" && <GalleryView />}
        {view === "sessions" && <SessionsView />}
        {view === "connectors" && <ConnectorsView />}
      </main>

      {/* Central Island - replaces FAB */}
      <CentralIsland
        onSendMessage={(message) => {
          setView("main")
          setInputPrompt(message)
          generateContent(message)
        }}
        onVoiceToggle={() => {
          console.log("Voice mode toggled")
          // TODO: Implement voice mode
        }}
      />
    </div>
  );
}
