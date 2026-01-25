// EXTRACTED from app/page.tsx lines 30-79, 81-87, 97
// Type definitions for widgets and UI components

/**
 * Widget descriptor interface - defines all possible widget properties
 * Uses optional properties to support different widget types
 */
export interface UIDescriptor {
  // Core identification
  descriptor_id: string;
  descriptor_type: WidgetType;
  title?: string;
  content?: string;

  // Form widget fields
  fields?: Array<{
    name: string;
    type: string;
    label: string;
    required: boolean;
    options?: string[];
  }>;
  // Backend sends form_fields (preferred name)
  form_fields?: Array<{
    label: string;
    type: string;
    description?: string;
    required: boolean;
    options?: string[];
  }>;
  submit_button_text?: string;

  // Progress widget fields
  task_name?: string;
  progress_percent?: number;
  status_text?: string;
  progress?: number;

  // Action/Confirmation widget fields
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

  // Multi-hop search fields
  hops_completed?: number;
  total_hops?: number;
  reflection_reasoning?: string;
  eta_seconds?: number;

  // Citation widget fields
  citations?: Array<{
    cited_text: string;
    document_index: number;
    document_title?: string;
    url?: string;
  }>;

  // Hop progress widget fields
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
}

/**
 * Session interface for session management
 */
export interface Session {
  id?: string;
  session_id?: string;
  title: string;
  created_at?: string;
  date?: string;
}

/**
 * View type for main navigation
 */
export type View = "main" | "gallery" | "sessions" | "connectors";

/**
 * Widget view state - controls how widget is displayed
 */
export type ViewState = "island" | "card" | "full";

/**
 * Position interface for widget coordinates
 */
export interface Position {
  x: number;
  y: number;
}

/**
 * QA checkpoint status for tracking generation progress
 */
export type QACheckpointStatus = "running" | "passed" | "failed";

/**
 * Widget type discriminator - all possible widget types from backend
 */
export type WidgetType =
  | "markdown"
  | "card"
  | "form"
  | "progress"
  | "action"
  | "confirmation"
  | "image"
  | "gallery"
  | "chart"
  | "search-result"
  | "hop-progress"
  | "citation-card";

/**
 * Incoming WebSocket widget data from backend
 * Backend sends "descriptor_type", but we also support "type" for legacy compatibility
 */
export interface WebSocketWidgetData {
  id?: string;
  descriptor_type?: WidgetType;
  type?: WidgetType;  // Legacy field for compatibility
  title?: string;
  content?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Extract widget type from WebSocket data with proper typing
 * Backend sends "descriptor_type", fallback to "type", default to "markdown"
 */
export function extractWidgetType(data: WebSocketWidgetData): WidgetType {
  // Prefer descriptor_type from backend, fallback to legacy type field
  return data.descriptor_type ?? data.type ?? "markdown";
}

/**
 * Type guard to check if unknown data is valid WebSocketWidgetData
 */
export function isWebSocketWidgetData(data: unknown): data is WebSocketWidgetData {
  if (typeof data !== "object" || data === null) {
    return false;
  }
  const widgetData = data as Record<string, unknown>;
  return (
    (typeof widgetData.id === "string" || widgetData.id === undefined) &&
    (typeof widgetData.descriptor_type === "string" || widgetData.descriptor_type === undefined) &&
    (typeof widgetData.type === "string" || widgetData.type === undefined)
  );
}

