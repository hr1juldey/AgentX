import type { UIDescriptor } from "@/types/widget-types";

/**
 * Helper to detect X-axis key (string column) from chart data
 * @returns The key name for the X-axis (e.g., "month", "year", "name")
 */
export function detectXAxisKey(data: Array<Record<string, string | number>>): string {
  if (!data || data.length === 0) return "month";
  const firstItem = data[0];
  const keys = Object.keys(firstItem);

  // Common label keys
  const labelKeys = new Set(["month", "year", "name", "label", "category", "date"]);

  // Find the first key that has a string value or is a common label key
  for (const key of keys) {
    if (labelKeys.has(key.toLowerCase()) || typeof firstItem[key] === "string") {
      return key;
    }
  }

  return keys[0] || "month";
}

/**
 * Helper to detect value keys (numeric columns) from chart data
 * @param data - Chart data array
 * @param xAxisKey - The key used for X-axis (will be excluded)
 * @returns Array of numeric value keys
 */
export function detectValueKeys(
  data: Array<Record<string, string | number>>,
  xAxisKey: string
): string[] {
  if (!data || data.length === 0) return ["value"];
  const firstItem = data[0];
  const keys = Object.keys(firstItem);

  // Find numeric keys (excluding the X-axis key)
  const numericKeys = keys.filter(
    key => key !== xAxisKey && typeof firstItem[key] === "number"
  );

  return numericKeys.length > 0 ? numericKeys : ["value"];
}

/**
 * Extract chart data from UIDescriptor metadata
 * Handles both direct data property and nested metadata structure
 */
export function extractChartData(descriptor: UIDescriptor): {
  data: Array<Record<string, string | number>>;
  dataKeys?: string[];
  chartType: "bar" | "line" | "pie" | "area";
} {
  const chartType = (descriptor.metadata?.chartType as "bar" | "line" | "pie" | "area") || "bar";

  // Check for data in metadata.data (from backend)
  const metadataData = descriptor.metadata?.data as Array<Record<string, string | number>> | undefined;

  // Check for direct dataKeys in metadata
  const metadataDataKeys = descriptor.metadata?.data_keys as string[] | undefined;

  return {
    data: metadataData || [],
    dataKeys: metadataDataKeys,
    chartType,
  };
}
