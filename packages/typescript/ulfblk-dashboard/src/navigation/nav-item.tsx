import type { ReactNode } from "react";
import { cn } from "@ulfblk/ui";

export interface NavItemProps {
  label: string;
  icon?: ReactNode;
  badge?: string | number;
  href?: string;
  onClick?: () => void;
  active?: boolean;
  collapsed?: boolean;
  className?: string;
}

export function NavItem({
  label,
  icon,
  badge,
  href,
  onClick,
  active = false,
  collapsed = false,
  className,
}: NavItemProps) {
  const baseClasses = cn(
    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
    "hover:bg-[hsl(var(--bloque-accent))] hover:text-[hsl(var(--bloque-accent-foreground))]",
    active
      ? "bg-[hsl(var(--bloque-accent))] text-[hsl(var(--bloque-accent-foreground))]"
      : "text-[hsl(var(--bloque-muted-foreground))]",
    collapsed && "justify-center px-2",
    className,
  );

  const content = (
    <>
      {icon && (
        <span className="flex h-5 w-5 shrink-0 items-center justify-center">
          {icon}
        </span>
      )}
      {!collapsed && <span className="truncate">{label}</span>}
      {!collapsed && badge != null && (
        <span className="ml-auto inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-[hsl(var(--bloque-primary))] px-1.5 text-xs font-medium text-[hsl(var(--bloque-primary-foreground))]">
          {badge}
        </span>
      )}
    </>
  );

  if (href) {
    return (
      <a href={href} className={baseClasses} aria-current={active ? "page" : undefined}>
        {content}
      </a>
    );
  }

  return (
    <button type="button" onClick={onClick} className={cn(baseClasses, "w-full text-left")} aria-current={active ? "page" : undefined}>
      {content}
    </button>
  );
}
