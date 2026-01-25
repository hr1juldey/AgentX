"use client";

import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/showcase/theme-toggle";
import { MessageSquare, Images, History, Database, X } from "lucide-react";
import { motion } from "framer-motion";
import type { View } from "@/types/widget-types";

export interface SidebarProps {
  sidebarOpen: boolean;
  currentView: View;
  onCloseSidebar: () => void;
  onNavMain: () => void;
  onNavGallery: () => void;
  onNavSessions: () => void;
  onNavConnectors: () => void;
}

/**
 * Sidebar - Navigation sidebar with view selection buttons
 * Animated slide-in/out based on sidebarOpen state
 */
export function Sidebar({
  sidebarOpen,
  currentView,
  onCloseSidebar,
  onNavMain,
  onNavGallery,
  onNavSessions,
  onNavConnectors,
}: SidebarProps) {
  return (
    <motion.aside
      initial={{ x: -320 }}
      animate={{ x: sidebarOpen ? 0 : -320 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="fixed left-0 top-0 h-full w-80 bg-card border-r border-border z-40 flex flex-col"
    >
      <div className="p-4 border-b border-border flex items-center justify-between">
        <h2 className="font-semibold text-lg">Navigation</h2>
        <Button variant="ghost" size="icon" onClick={onCloseSidebar}>
          <X className="w-5 h-5" />
        </Button>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        <Button
          variant={currentView === "main" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={onNavMain}
        >
          <MessageSquare className="w-4 h-4 mr-2" />
          Main Workspace
        </Button>
        <Button
          variant={currentView === "gallery" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={onNavGallery}
        >
          <Images className="w-4 h-4 mr-2" />
          Widget Gallery
        </Button>
        <Button
          variant={currentView === "sessions" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={onNavSessions}
        >
          <History className="w-4 h-4 mr-2" />
          Sessions
        </Button>
        <Button
          variant={currentView === "connectors" ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={onNavConnectors}
        >
          <Database className="w-4 h-4 mr-2" />
          Connectors
        </Button>
      </nav>

      <div className="p-4 border-t border-border">
        <ThemeToggle />
      </div>
    </motion.aside>
  );
}
