import { useState, useCallback, type ReactNode } from "react";
import { cn } from "@bloque/ui";
import { useClickOutside } from "../hooks/use-click-outside.js";
import { useEscapeKey } from "../hooks/use-keyboard.js";

export interface TenantOption {
  id: string;
  name: string;
  slug?: string;
  icon?: ReactNode;
}

export interface TenantSelectorProps {
  tenants: TenantOption[];
  currentTenantId?: string | null;
  onSelect?: (tenantId: string) => void;
  className?: string;
}

export function TenantSelector({
  tenants,
  currentTenantId,
  onSelect,
  className,
}: TenantSelectorProps) {
  const [open, setOpen] = useState(false);

  const close = useCallback(() => setOpen(false), []);
  const dropdownRef = useClickOutside<HTMLDivElement>(close);
  useEscapeKey(close);

  const currentTenant = tenants.find((t) => t.id === currentTenantId);

  if (tenants.length === 0) {
    return null;
  }

  return (
    <div ref={dropdownRef} className={cn("relative", className)}>
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex w-full items-center gap-2 rounded-md border border-[hsl(var(--bloque-border))] px-3 py-2 text-sm hover:bg-[hsl(var(--bloque-accent))] transition-colors"
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        {currentTenant?.icon && (
          <span className="flex h-5 w-5 shrink-0 items-center justify-center">
            {currentTenant.icon}
          </span>
        )}
        <span className="truncate text-[hsl(var(--bloque-foreground))]">
          {currentTenant?.name ?? "Select tenant"}
        </span>
        <span className="ml-auto text-[hsl(var(--bloque-muted-foreground))]" aria-hidden="true">
          v
        </span>
      </button>
      {open && (
        <div
          className="absolute left-0 top-full z-50 mt-1 w-full rounded-md border border-[hsl(var(--bloque-border))] bg-[hsl(var(--bloque-card))] py-1 shadow-lg"
          role="listbox"
          aria-label="Select tenant"
        >
          {tenants.map((tenant) => (
            <button
              key={tenant.id}
              type="button"
              role="option"
              aria-selected={tenant.id === currentTenantId}
              onClick={() => {
                onSelect?.(tenant.id);
                setOpen(false);
              }}
              className={cn(
                "flex w-full items-center gap-2 px-3 py-2 text-left text-sm transition-colors",
                tenant.id === currentTenantId
                  ? "bg-[hsl(var(--bloque-accent))] text-[hsl(var(--bloque-accent-foreground))]"
                  : "text-[hsl(var(--bloque-foreground))] hover:bg-[hsl(var(--bloque-muted))]",
              )}
            >
              {tenant.icon && (
                <span className="flex h-5 w-5 shrink-0 items-center justify-center">
                  {tenant.icon}
                </span>
              )}
              <span className="truncate">{tenant.name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
