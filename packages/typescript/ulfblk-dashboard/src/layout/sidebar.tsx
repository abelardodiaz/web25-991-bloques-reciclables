import type { ReactNode } from "react";
import { cn } from "@ulfblk/ui";
import { useDashboardContext } from "../context/dashboard-context.js";

export interface SidebarProps {
  header?: ReactNode;
  footer?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function Sidebar({
  header,
  footer,
  children,
  className,
}: SidebarProps) {
  const { sidebarCollapsed, mobileMenuOpen, setMobileMenuOpen } =
    useDashboardContext();

  const width = sidebarCollapsed ? "4rem" : "16rem";

  return (
    <>
      {/* Mobile overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 sm:hidden"
          onClick={() => setMobileMenuOpen(false)}
          onKeyDown={(e) => {
            if (e.key === "Escape") setMobileMenuOpen(false);
          }}
          role="button"
          tabIndex={-1}
          aria-label="Close menu"
        />
      )}

      {/* Sidebar */}
      <aside
        style={{ width }}
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex flex-col border-r border-[hsl(var(--bloque-border))] bg-[hsl(var(--bloque-card))] transition-all duration-200",
          "max-sm:translate-x-[-100%]",
          mobileMenuOpen && "max-sm:translate-x-0 max-sm:w-64",
          "sm:relative sm:z-auto",
          className,
        )}
      >
        {header && (
          <div className="flex h-14 items-center border-b border-[hsl(var(--bloque-border))] px-4">
            {header}
          </div>
        )}
        <nav className="flex-1 overflow-y-auto px-2 py-2">
          {children}
        </nav>
        {footer && (
          <div className="border-t border-[hsl(var(--bloque-border))] px-4 py-3">
            {footer}
          </div>
        )}
      </aside>
    </>
  );
}
