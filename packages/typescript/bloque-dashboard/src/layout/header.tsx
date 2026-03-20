import type { ReactNode } from "react";
import { cn } from "@bloque/ui";
import { useDashboardContext } from "../context/dashboard-context.js";

export interface HeaderProps {
  breadcrumbs?: ReactNode;
  actions?: ReactNode;
  className?: string;
}

export function Header({
  breadcrumbs,
  actions,
  className,
}: HeaderProps) {
  const { toggleMobileMenu } = useDashboardContext();

  return (
    <header
      className={cn(
        "flex h-14 items-center gap-4 border-b border-[hsl(var(--bloque-border))] bg-[hsl(var(--bloque-background))] px-4 sm:px-6",
        className,
      )}
    >
      <button
        type="button"
        onClick={toggleMobileMenu}
        className="rounded-md p-1.5 hover:bg-[hsl(var(--bloque-accent))] sm:hidden"
        aria-label="Toggle menu"
      >
        <span className="block h-5 w-5 text-center leading-5">=</span>
      </button>
      {breadcrumbs && <div className="flex-1">{breadcrumbs}</div>}
      {!breadcrumbs && <div className="flex-1" />}
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </header>
  );
}
