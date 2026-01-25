import { useCallback } from "react";
import { API_CONFIG } from "@/constants/widget-constants";
import type { UIDescriptor } from "@/types/widget-types";

interface UseContentGenerationOptions {
  setLoading: (loading: boolean) => void;
  setWidgets: React.Dispatch<React.SetStateAction<UIDescriptor[]>>;
}

/**
 * Hook for content generation via the backend API
 * Handles widget generation and adds them to the widgets state
 *
 * @param options - Configuration options
 * @returns Object containing generateContent function
 */
export function useContentGeneration({
  setLoading,
  setWidgets,
}: UseContentGenerationOptions) {
  /**
   * Generate content/widgets from the backend API
   * @param prompt - User prompt for content generation
   * @param widgetType - Optional widget type hint
   */
  const generateContent = useCallback(
    async (prompt: string, widgetType?: string) => {
      if (!prompt.trim()) return;

      console.log("🟢 generateContent called:", { prompt, widgetType });
      setLoading(true);
      try {
        console.log("🟢 Fetching from:", `${API_CONFIG.URL}/api/v1/generate-widget`);
        const res = await fetch(`${API_CONFIG.URL}/api/v1/generate-widget`, {
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
    },
    [setLoading, setWidgets]
  );

  return { generateContent };
}
