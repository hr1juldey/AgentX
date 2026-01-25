import { useCallback } from "react";
import { useUIStore } from "@/store/ui-store";

/**
 * Custom hook for navigation handlers
 * Provides memoized callbacks for navigation and sidebar control
 */
export function useNavigation() {
  const setCurrentView = useUIStore((s) => s.setCurrentView);
  const setSidebarOpen = useUIStore((s) => s.setSidebarOpen);
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);

  const handleCloseSidebar = useCallback(() => setSidebarOpen(false), [setSidebarOpen]);

  const handleToggleSidebar = useCallback(() => toggleSidebar(), [toggleSidebar]);

  const handleNavMain = useCallback(() => {
    setCurrentView("main");
    setSidebarOpen(false);
  }, [setCurrentView, setSidebarOpen]);

  const handleNavGallery = useCallback(() => {
    setCurrentView("gallery");
    setSidebarOpen(false);
  }, [setCurrentView, setSidebarOpen]);

  const handleNavSessions = useCallback(() => {
    setCurrentView("sessions");
    setSidebarOpen(false);
  }, [setCurrentView, setSidebarOpen]);

  const handleNavConnectors = useCallback(() => {
    setCurrentView("connectors");
    setSidebarOpen(false);
  }, [setCurrentView, setSidebarOpen]);

  return {
    handleCloseSidebar,
    handleToggleSidebar,
    handleNavMain,
    handleNavGallery,
    handleNavSessions,
    handleNavConnectors,
  };
}
