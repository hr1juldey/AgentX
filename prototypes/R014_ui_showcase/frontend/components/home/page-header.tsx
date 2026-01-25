"use client";

import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { API_CONFIG } from "@/constants/widget-constants";

export interface PageHeaderProps {
  health: 'unknown' | 'healthy' | 'unhealthy' | 'disconnected';
  onToggleSidebar: () => void;
}

/**
 * PageHeader - Fixed header with sidebar toggle and health status indicator
 */
export function PageHeader({ health, onToggleSidebar }: PageHeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 h-16 border-b border-border bg-card/80 backdrop-blur-sm z-30 flex items-center px-4 lg:px-6">
      <Button
        variant="ghost"
        size="icon"
        onClick={onToggleSidebar}
        className="mr-4"
      >
        <Plus className="w-5 h-5" />
      </Button>
      <h1 className="text-xl font-semibold">{API_CONFIG.APP_NAME}</h1>
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
  );
}
