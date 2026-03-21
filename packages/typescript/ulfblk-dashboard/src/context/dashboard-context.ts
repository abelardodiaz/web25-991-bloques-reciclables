import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import { jsx } from "react/jsx-runtime";

export interface DashboardContextValue {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  mobileMenuOpen: boolean;
  toggleMobileMenu: () => void;
  setMobileMenuOpen: (open: boolean) => void;
}

const DashboardContext = createContext<DashboardContextValue | null>(null);

export interface DashboardProviderProps {
  children: ReactNode;
  defaultCollapsed?: boolean;
}

export function DashboardProvider({
  children,
  defaultCollapsed = false,
}: DashboardProviderProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(defaultCollapsed);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed((prev) => !prev);
  }, []);

  const toggleMobileMenu = useCallback(() => {
    setMobileMenuOpen((prev) => !prev);
  }, []);

  const value: DashboardContextValue = {
    sidebarCollapsed,
    toggleSidebar,
    setSidebarCollapsed,
    mobileMenuOpen,
    toggleMobileMenu,
    setMobileMenuOpen,
  };

  return jsx(DashboardContext.Provider, { value, children });
}

export function useDashboardContext(): DashboardContextValue {
  const ctx = useContext(DashboardContext);
  if (!ctx) {
    throw new Error("useDashboardContext must be used within a DashboardProvider");
  }
  return ctx;
}
