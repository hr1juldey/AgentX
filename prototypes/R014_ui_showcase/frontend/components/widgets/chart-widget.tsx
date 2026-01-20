"use client"
import { memo } from "react"

import { motion } from "framer-motion"
import { X } from "lucide-react"
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
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
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
  onDismiss,
  dragPosition,
  onDragEnd
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
      drag
      dragElastic={0.2}
      dragMomentum={false}
      dragConstraints={{ left: -500, right: 500, top: -500, bottom: 500 }}
      whileDrag={{ scale: 1.02, rotate: 1, cursor: "grabbing", zIndex: 50 }}
      onDragEnd={(_, info) => onDragEnd?.(
        (dragPosition?.x || 0) + info.offset.x,
        (dragPosition?.y || 0) + info.offset.y
      )}
      style={{ x: dragPosition?.x || 0, y: dragPosition?.y || 0 }}
      className="relative bg-card cursor-grab shadow-lg hover:shadow-xl border border-border rounded-lg p-6 min-w-[600px]"
    >
      {onDismiss && (
        <button
          onClick={() => onDismiss?.()}
          className="absolute top-2 right-2 p-1 rounded hover:bg-muted transition-colors"
          aria-label="Dismiss"
        >
          <X className="w-4 h-4" />
        </button>
      )}

      {title && <h3 className="text-lg font-semibold mb-2">{title}</h3>}
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
    </motion.div>
  )
});
