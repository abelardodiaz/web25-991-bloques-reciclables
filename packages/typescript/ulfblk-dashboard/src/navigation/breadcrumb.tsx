import type { ReactNode } from "react";
import { cn } from "@ulfblk/ui";

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: ReactNode;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  separator?: ReactNode;
  className?: string;
}

export function Breadcrumb({
  items,
  separator = "/",
  className,
}: BreadcrumbProps) {
  if (items.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className={cn("flex items-center gap-1.5 text-sm", className)}>
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <div key={`${item.label}-${index}`} className="flex items-center gap-1.5">
            {index > 0 && (
              <span className="text-[hsl(var(--bloque-muted-foreground))]" aria-hidden="true">
                {separator}
              </span>
            )}
            {item.icon && (
              <span className="flex h-4 w-4 items-center justify-center">
                {item.icon}
              </span>
            )}
            {isLast || !item.href ? (
              <span
                className={cn(
                  isLast
                    ? "font-medium text-[hsl(var(--bloque-foreground))]"
                    : "text-[hsl(var(--bloque-muted-foreground))]",
                )}
                aria-current={isLast ? "page" : undefined}
              >
                {item.label}
              </span>
            ) : (
              <a
                href={item.href}
                className="text-[hsl(var(--bloque-muted-foreground))] hover:text-[hsl(var(--bloque-foreground))] transition-colors"
              >
                {item.label}
              </a>
            )}
          </div>
        );
      })}
    </nav>
  );
}
