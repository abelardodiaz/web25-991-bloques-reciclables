import { useState, type ReactNode } from "react";
import { cn } from "@bloque/ui";

export interface NavSectionProps {
  heading?: string;
  children: ReactNode;
  collapsible?: boolean;
  defaultOpen?: boolean;
  collapsed?: boolean;
  className?: string;
}

export function NavSection({
  heading,
  children,
  collapsible = false,
  defaultOpen = true,
  collapsed = false,
  className,
}: NavSectionProps) {
  const [open, setOpen] = useState(defaultOpen);

  if (collapsed) {
    return (
      <div className={cn("space-y-1 py-2", className)}>
        {heading && (
          <div className="mx-auto my-1 h-px w-4 bg-[hsl(var(--bloque-border))]" />
        )}
        {children}
      </div>
    );
  }

  return (
    <div className={cn("space-y-1 py-2", className)}>
      {heading && (
        collapsible ? (
          <button
            type="button"
            onClick={() => setOpen((prev) => !prev)}
            className="flex w-full items-center justify-between px-3 py-1 text-xs font-semibold uppercase tracking-wider text-[hsl(var(--bloque-muted-foreground))]"
            aria-expanded={open}
          >
            <span>{heading}</span>
            <span className={cn("transition-transform", open ? "rotate-0" : "-rotate-90")}>
              {"v"}
            </span>
          </button>
        ) : (
          <div className="px-3 py-1 text-xs font-semibold uppercase tracking-wider text-[hsl(var(--bloque-muted-foreground))]">
            {heading}
          </div>
        )
      )}
      {(!collapsible || open) && children}
    </div>
  );
}
