"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, MessageSquare, X, Sparkles, Images, History, Database } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ThemeToggle } from "@/components/showcase/theme-toggle";
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

  // Generate content
  const generateContent = async (prompt: string, widgetType?: string) => {
    if (!prompt.trim()) return;

    setLoading(true);
    try {
      const res = await fetch(`${apiUrl}/api/v1/mock/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          widget_type: widgetType || "markdown",
        }),
      });
      const data = await res.json();
      // Map backend response to frontend format
      const widget: UIDescriptor = {
        descriptor_id: data.id,
        descriptor_type: data.type,
        title: data.title,
        content: data.content,
        dismissible: data.dismissible ?? true,
        // Extract metadata fields
        ...(data.metadata?.fields && { fields: data.metadata.fields }),
        ...(data.metadata?.submit_label && { submit_button_text: data.metadata.submit_label }),
        ...(data.metadata?.status_text && { status_text: data.metadata.status_text }),
        ...(data.metadata?.value !== undefined && { progress_percent: data.metadata.value * 100 }),
        ...(data.metadata?.button_text && { button_text: data.metadata.button_text }),
        ...(data.metadata?.action_id && { action_id: data.metadata.action_id }),
        ...(data.metadata?.confirm_label && { confirm_label: data.metadata.confirm_label }),
        ...(data.metadata?.cancel_label && { cancel_label: data.metadata.cancel_label }),
      };
      setWidgets((prev) => [widget, ...prev]);
      setInputPrompt(""); // Clear input after successful generation
    } catch (error) {
      console.error("Failed to generate content:", error);
    }
    setLoading(false);
  };

  // Dismiss widget
  const dismissWidget = (id: string) => {
    setWidgets((prev) => prev.filter((w) => w.descriptor_id !== id));
  };

  // Update widget position after drag
  const updateWidgetPosition = (id: string, x: number, y: number) => {
    setWidgets((prev) =>
      prev.map((w) =>
        w.descriptor_id === id ? { ...w, x, y } : w
      )
    );
  };

  // Render widget based on type
  const renderWidget = (descriptor: UIDescriptor) => {
    const onDismiss = () => dismissWidget(descriptor.descriptor_id);
    const dragPosition = descriptor.x !== undefined || descriptor.y !== undefined
      ? { x: descriptor.x || 0, y: descriptor.y || 0 }
      : undefined;
    const onDragEnd = (x: number, y: number) => updateWidgetPosition(descriptor.descriptor_id, x, y);

    switch (descriptor.descriptor_type) {
      case "markdown":
        return descriptor.content ? (
          <MarkdownWidget
            key={descriptor.descriptor_id}
            content={descriptor.content}
            onDismiss={onDismiss}
            dragPosition={dragPosition}
            onDragEnd={onDragEnd}
          />
        ) : null;
      case "card":
        return (
          <CardWidget
            key={descriptor.descriptor_id}
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
            key={descriptor.descriptor_id}
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
            key={descriptor.descriptor_id}
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
            key={descriptor.descriptor_id}
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
            key={descriptor.descriptor_id}
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
            key={descriptor.descriptor_id}
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
            key={descriptor.descriptor_id}
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
            key={descriptor.descriptor_id}
            title={descriptor.title}
            content={descriptor.content}
            onDismiss={onDismiss}
            dragPosition={dragPosition}
            onDragEnd={onDragEnd}
          />
        );
      default:
        return null;
    }
  };

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
            Enter a prompt below to generate dynamic content using DSPy and Ollama.
            The backend will select the appropriate widget type and generate content for it.
          </p>
        </CardContent>
      </Card>

      {/* Input Form */}
      <Card>
        <CardHeader>
          <CardTitle>Generate Content</CardTitle>
          <CardDescription>
            Describe what you want to see, and the AI will create an appropriate widget
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              placeholder="e.g., 'Explain quantum computing', 'What's the weather?', 'Create a survey form'"
              value={inputPrompt}
              onChange={(e) => setInputPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && inputPrompt.trim() && !loading) {
                  generateContent(inputPrompt);
                }
              }}
              disabled={loading}
              autoFocus
            />
            <Button
              onClick={() => {
                if (inputPrompt.trim()) {
                  generateContent(inputPrompt);
                }
              }}
              disabled={loading || !inputPrompt.trim()}
            >
              {loading ? "Generating..." : "Generate"}
            </Button>
          </div>

          {/* Quick Actions */}
          <div className="mt-4 flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setInputPrompt("Explain the benefits of meditation");
                setTimeout(() => generateContent("Explain the benefits of meditation", "markdown"), 100);
              }}
              disabled={loading}
            >
              Markdown Demo
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setInputPrompt("Travel tips for Japan");
                setTimeout(() => generateContent("Travel tips for Japan", "card"), 100);
              }}
              disabled={loading}
            >
              Card Demo
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setInputPrompt("User feedback form");
                setTimeout(() => generateContent("User feedback form", "form"), 100);
              }}
              disabled={loading}
            >
              Form Demo
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setInputPrompt("Loading data");
                setTimeout(() => generateContent("Loading data", "progress"), 100);
              }}
              disabled={loading}
            >
              Progress Demo
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setInputPrompt("Beautiful landscape photo");
                setTimeout(() => generateContent("Beautiful landscape photo", "image"), 100);
              }}
              disabled={loading}
            >
              Image Demo
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setInputPrompt("Photo gallery of nature");
                setTimeout(() => generateContent("Photo gallery of nature", "gallery"), 100);
              }}
              disabled={loading}
            >
              Gallery Demo
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setInputPrompt("Sales data chart");
                setTimeout(() => generateContent("Sales data chart", "chart"), 100);
              }}
              disabled={loading}
            >
              Chart Demo
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Generated Widgets */}
      <AnimatePresence mode="popLayout">
        {widgets.map((widget) => renderWidget(widget))}
      </AnimatePresence>

      {widgets.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="py-12 text-center">
            <MessageSquare className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
            <p className="text-muted-foreground">
              No widgets yet. Enter a prompt above to generate your first widget.
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

      {/* FAB */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        className="fixed bottom-6 right-6 z-50"
      >
        <Button
          size="lg"
          className="rounded-full w-14 h-14 shadow-lg"
          onClick={() => {
            setView("main");
            setInputPrompt("");
            setWidgets([]);
          }}
        >
          <Plus className="w-6 h-6" />
        </Button>
      </motion.div>
    </div>
  );
}
