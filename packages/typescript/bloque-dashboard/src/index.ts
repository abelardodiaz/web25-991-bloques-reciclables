// Context
export { DashboardProvider } from "./context/dashboard-context.js";
export type {
  DashboardProviderProps,
  DashboardContextValue,
} from "./context/dashboard-context.js";

// Hooks
export { useSidebar } from "./hooks/use-sidebar.js";
export type { UseSidebarReturn } from "./hooks/use-sidebar.js";
export { useClickOutside } from "./hooks/use-click-outside.js";
export { useEscapeKey } from "./hooks/use-keyboard.js";

// Layout
export { DashboardLayout } from "./layout/dashboard-layout.js";
export type { DashboardLayoutProps } from "./layout/dashboard-layout.js";
export { Sidebar } from "./layout/sidebar.js";
export type { SidebarProps } from "./layout/sidebar.js";
export { Header } from "./layout/header.js";
export type { HeaderProps } from "./layout/header.js";
export { PageContainer } from "./layout/page-container.js";
export type { PageContainerProps } from "./layout/page-container.js";

// Navigation
export { NavItem } from "./navigation/nav-item.js";
export type { NavItemProps } from "./navigation/nav-item.js";
export { NavSection } from "./navigation/nav-section.js";
export type { NavSectionProps } from "./navigation/nav-section.js";
export { Breadcrumb } from "./navigation/breadcrumb.js";
export type { BreadcrumbProps, BreadcrumbItem } from "./navigation/breadcrumb.js";

// Data display
export { StatCard } from "./data/stat-card.js";
export type { StatCardProps, TrendDirection } from "./data/stat-card.js";
export { DataTable } from "./data/data-table.js";
export type {
  DataTableProps,
  ColumnDef,
  SortDirection,
} from "./data/data-table.js";
export { EmptyState } from "./data/empty-state.js";
export type { EmptyStateProps } from "./data/empty-state.js";

// User
export { UserMenu } from "./user/user-menu.js";
export type { UserMenuProps, UserMenuUser } from "./user/user-menu.js";
export { TenantSelector } from "./user/tenant-selector.js";
export type {
  TenantSelectorProps,
  TenantOption,
} from "./user/tenant-selector.js";
