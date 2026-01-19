"use client"

import * as LucideIcons from "lucide-react"
import { cn } from "@/lib/utils"

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  search: LucideIcons.Search,
  info: LucideIcons.Info,
  cpu: LucideIcons.Cpu,
  cloud: LucideIcons.Cloud,
  sparkles: LucideIcons.Sparkles,
  settings: LucideIcons.Settings,
  home: LucideIcons.Home,
  gallery: LucideIcons.Image,
  history: LucideIcons.History,
  database: LucideIcons.Database,
}

interface LucideIconProps {
  name: string
  className?: string
}

export function LucideIcon({ name, className }: LucideIconProps) {
  const Icon = iconMap[name] || LucideIcons.HelpCircle

  return <Icon className={cn("w-5 h-5", className)} />
}

export { iconMap }
