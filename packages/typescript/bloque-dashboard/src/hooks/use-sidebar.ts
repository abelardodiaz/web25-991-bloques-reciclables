import { useDashboardContext } from "../context/dashboard-context.js";

export interface UseSidebarReturn {
  collapsed: boolean;
  toggle: () => void;
  setCollapsed: (collapsed: boolean) => void;
}

export function useSidebar(): UseSidebarReturn {
  const { sidebarCollapsed, toggleSidebar, setSidebarCollapsed } =
    useDashboardContext();

  return {
    collapsed: sidebarCollapsed,
    toggle: toggleSidebar,
    setCollapsed: setSidebarCollapsed,
  };
}
