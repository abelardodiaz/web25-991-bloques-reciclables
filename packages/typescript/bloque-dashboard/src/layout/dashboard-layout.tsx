import type { ReactNode } from "react";
import { cn } from "@bloque/ui";
import {
  DashboardProvider,
  type DashboardProviderProps,
} from "../context/dashboard-context.js";

export interface DashboardLayoutProps
  extends Omit<DashboardProviderProps, "children"> {
  sidebar: ReactNode;
  header?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function DashboardLayout({
  sidebar,
  header,
  children,
  defaultCollapsed,
  className,
}: DashboardLayoutProps) {
  return (
    <DashboardProvider defaultCollapsed={defaultCollapsed}>
      <div className={cn("flex h-screen overflow-hidden bg-[hsl(var(--bloque-background))]", className)}>
        {sidebar}
        <div className="flex flex-1 flex-col overflow-hidden">
          {header}
          <main className="flex-1 overflow-y-auto">
            {children}
          </main>
        </div>
      </div>
    </DashboardProvider>
  );
}
