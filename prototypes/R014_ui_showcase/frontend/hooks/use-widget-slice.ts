"use client";

import { useSyncExternalStore } from "react";
import { useWidgetStore } from "@/store/widget-store";

/**
 * Custom hook to subscribe to a single widget's atomic slice
 * This prevents cascade re-renders when OTHER widgets change
 *
 * @param key - The Zustand store key to subscribe to (e.g., "widget_mock-card-001_data")
 * @returns The current value of the slice, or undefined if not found
 *
 * Example:
 *   const widget = useWidgetSlice<UIDescriptor>("widget_mock-card-001_data");
 *   const viewState = useWidgetSlice<ViewState>("widget_mock-card-001_viewState");
 */
export function useWidgetSlice<T>(key: string): T | undefined {
  // Extract widget ID from key for logging (e.g., "widget_mock-card-001_data" -> "mock-card-001")
  const widgetIdMatch = key.match(/widget_([^_]+)_/);
  const widgetId = widgetIdMatch ? widgetIdMatch[1] : key;

  return useSyncExternalStore(
    (callback) => {
      // Subscribe only to changes in this specific slice
      const unsubscribe = useWidgetStore.subscribe((state, prevState) => {
        const currentValue = state[key] as T;
        const previousValue = prevState[key] as T;

        // DIAGNOSTIC: Log every subscription notification for this widget
        console.log(`[useWidgetSlice ${widgetId}] Key="${key}"`, {
          'current === previous': currentValue === previousValue,
          'current': currentValue,
          'previous': previousValue,
          'willCallback': currentValue !== previousValue
        });

        // Only trigger callback if THIS slice changed
        if (currentValue !== previousValue) {
          callback();
        }
      });
      return unsubscribe;
    },
    () => useWidgetStore.getState()[key] as T,
    () => useWidgetStore.getState()[key] as T
  );
}
