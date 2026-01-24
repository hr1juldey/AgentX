"use client"
import { memo, useCallback } from "react"

import { motion, AnimatePresence } from "framer-motion"
import { X, BarChart3, ChevronDown } from "lucide-react"
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts"

interface ChartWidgetProps {
  title?: string
  content?: string
  chartType?: "bar" | "line" | "pie" | "area"
  data?: Array<Record<string, string | number>>
  dataKeys?: string[]
  colors?: string[]
  collapsed?: boolean
  onToggleCollapse?: () => void
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
  disableDrag?: boolean // When true, widget is not draggable (for embedded use in IsolatedWidget)
}

const DEFAULT_COLORS = [
  "hsl(var(--primary))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
]

const DEFAULT_DATA = [
  { month: "Jan", value: 400, target: 300 },
  { month: "Feb", value: 300, target: 350 },
  { month: "Mar", value: 600, target: 400 },
  { month: "Apr", value: 800, target: 500 },
  { month: "May", value: 500, target: 600 },
  { month: "Jun", value: 700, target: 650 },
]

// Helper to detect X-axis key (string column)
const detectXAxisKey = (data: Array<Record<string, string | number>>): string => {
  if (!data || data.length === 0) return "month"
  const firstItem = data[0]
  const keys = Object.keys(firstItem)

  // Common label keys
  const labelKeys = new Set(["month", "year", "name", "label", "category", "date"])

  // Find the first key that has a string value or is a common label key
  for (const key of keys) {
    if (labelKeys.has(key.toLowerCase()) || typeof firstItem[key] === "string") {
      return key
    }
  }

  return keys[0] || "month"
}

// Helper to detect value keys (numeric columns)
const detectValueKeys = (
  data: Array<Record<string, string | number>>,
  xAxisKey: string
): string[] => {
  if (!data || data.length === 0) return ["value"]
  const firstItem = data[0]
  const keys = Object.keys(firstItem)

  // Find numeric keys (excluding the X-axis key)
  const numericKeys = keys.filter(
    key => key !== xAxisKey && typeof firstItem[key] === "number"
  )

  return numericKeys.length > 0 ? numericKeys : ["value"]
}

export const ChartWidget = memo(function ChartWidget({
  title,
  content,
  chartType = "bar",
  data = DEFAULT_DATA,
  dataKeys,
  colors = DEFAULT_COLORS,
  collapsed = false,
  onToggleCollapse,
  onDismiss,
  dragPosition,
  onDragEnd,
  disableDrag = false
}: ChartWidgetProps) {
  // Simple, direct computation - no memoization
  const isValidData = Array.isArray(data) && data.length > 0

  // Detect X-axis and value keys
  const xAxisKey = isValidData ? detectXAxisKey(data) : "month"
  const effectiveDataKeys = isValidData && dataKeys && dataKeys.length > 0
    ? dataKeys
    : isValidData
    ? detectValueKeys(data, xAxisKey)
    : ["value", "target"]

  const handleDragEnd = useCallback((_: any, info: any) => {
    onDragEnd?.(
      (dragPosition?.x || 0) + info.offset.x,
      (dragPosition?.y || 0) + info.offset.y
    );
  }, [onDragEnd, dragPosition]);

  const handleDismiss = useCallback(() => {
    onDismiss?.();
  }, [onDismiss]);

  const renderChart = () => {
    const chartProps = {
      data,
      margin: { top: 5, right: 30, left: 20, bottom: 5 },
    }

    switch (chartType) {
      case "bar":
        return (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart {...chartProps}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey={xAxisKey} className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "0.5rem",
                }}
              />
              <Legend />
              {effectiveDataKeys.map((key, index) => (
                <Bar key={key} dataKey={key} fill={colors[index % colors.length]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        )

      case "line":
        return (
          <ResponsiveContainer width="100%" height={250}>
            <LineChart {...chartProps}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey={xAxisKey} className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "0.5rem",
                }}
              />
              <Legend />
              {effectiveDataKeys.map((key, index) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={colors[index % colors.length]}
                  strokeWidth={2}
                  dot={{ fill: colors[index % colors.length], r: 4 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )

      case "area":
        return (
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart {...chartProps}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey={xAxisKey} className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "0.5rem",
                }}
              />
              <Legend />
              {effectiveDataKeys.map((key, index) => (
                <Area
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={colors[index % colors.length]}
                  fill={colors[index % colors.length]}
                  fillOpacity={0.6}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        )

      case "pie":
        const pieData = data.map((item) => ({
          name: Object.values(item)[0] as string,
          value: Object.values(item)[1] as number,
        }))

        return (
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
                outerRadius={80}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "0.5rem",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        )

      default:
        return null
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.25 }}
      drag={disableDrag ? false : undefined}
      dragElastic={0.1}
      dragMomentum={false}
      dragConstraints={false}
      whileDrag={disableDrag ? undefined : { scale: 1.02, cursor: "grabbing", zIndex: 9999 }}
      onDragEnd={handleDragEnd}
      style={{ x: dragPosition?.x || 0, y: dragPosition?.y || 0 }}
      className="relative bg-card  shadow-lg hover:shadow-xl border border-border rounded-lg min-w-[600px]"
    >
      {/* Widget Header - Click to toggle (Jira-style) */}
      <div
        className="flex items-center justify-between px-4 py-2 border-b bg-muted/30 cursor-pointer hover:bg-muted/50"
        onClick={() => onToggleCollapse?.()}
      >
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium">{title || "Chart"}</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Chevron indicator - rotates based on collapsed state */}
          <motion.div
            animate={{ rotate: collapsed ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          </motion.div>

          {/* Dismiss button - stopPropagation to prevent collapse */}
          {onDismiss && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDismiss();
              }}
              className="p-1 rounded hover:bg-destructive/10 hover:text-destructive transition-colors"
              aria-label="Dismiss"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Chart Content - Collapsible with smart animation */}
      <AnimatePresence initial={false} mode="wait">
        {!collapsed && (
          <motion.div
            layout="position"
            initial={{ height: 0, opacity: 0, scaleY: 0.95 }}
            animate={{ height: "auto", opacity: 1, scaleY: 1 }}
            exit={{ height: 0, opacity: 0, scaleY: 0.95 }}
            transition={{
              height: { type: "spring", stiffness: 400, damping: 30 },
              opacity: { duration: 0.15 },
              scaleY: { type: "spring", stiffness: 400, damping: 30 }
            }}
            style={{ originY: 0 }}
            className="overflow-hidden"
          >
            <div className="p-6">
              {content && <p className="text-sm text-muted-foreground mb-4">{content}</p>}

              {/* Show chart if data is valid, otherwise show fallback */}
              {isValidData ? (
                <div className="w-full">{renderChart()}</div>
              ) : (
                <div className="w-full p-4 bg-muted/50 rounded-lg border border-dashed border-muted-foreground/50">
                  <p className="text-sm text-muted-foreground text-center">
                    {content || "Chart data is being generated..."}
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
});
