import type { ReactNode } from "react";
import { cn } from "@bloque/ui";

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-12 text-center", className)}>
      {icon && (
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-[hsl(var(--bloque-muted))] text-[hsl(var(--bloque-muted-foreground))]">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-semibold text-[hsl(var(--bloque-foreground))]">
        {title}
      </h3>
      {description && (
        <p className="mt-1 max-w-sm text-sm text-[hsl(var(--bloque-muted-foreground))]">
          {description}
        </p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
