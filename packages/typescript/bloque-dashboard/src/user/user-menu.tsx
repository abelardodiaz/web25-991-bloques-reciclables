import { useState, useCallback, type ReactNode } from "react";
import { cn } from "@bloque/ui";
import { useClickOutside } from "../hooks/use-click-outside.js";
import { useEscapeKey } from "../hooks/use-keyboard.js";

export interface UserMenuUser {
  userId: string;
  email?: string;
  name?: string;
  avatarUrl?: string;
  roles?: string[];
}

export interface UserMenuProps {
  user?: UserMenuUser | null;
  onLogout?: () => void;
  actions?: ReactNode;
  className?: string;
}

function getInitials(name?: string, email?: string): string {
  if (name) {
    return name
      .split(" ")
      .map((part) => part[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  }
  if (email) {
    return email[0].toUpperCase();
  }
  return "U";
}

export function UserMenu({
  user: userProp,
  onLogout,
  actions,
  className,
}: UserMenuProps) {
  const [open, setOpen] = useState(false);

  const close = useCallback(() => setOpen(false), []);
  const menuRef = useClickOutside<HTMLDivElement>(close);
  useEscapeKey(close);

  if (!userProp) {
    return null;
  }

  const initials = getInitials(
    userProp.name,
    userProp.email,
  );

  return (
    <div ref={menuRef} className={cn("relative", className)}>
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-[hsl(var(--bloque-accent))] transition-colors"
        aria-expanded={open}
        aria-haspopup="true"
      >
        {userProp.avatarUrl ? (
          <img
            src={userProp.avatarUrl}
            alt=""
            className="h-8 w-8 rounded-full"
          />
        ) : (
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[hsl(var(--bloque-primary))] text-xs font-medium text-[hsl(var(--bloque-primary-foreground))]">
            {initials}
          </span>
        )}
      </button>
      {open && (
        <div
          className="absolute right-0 top-full z-50 mt-1 w-56 rounded-md border border-[hsl(var(--bloque-border))] bg-[hsl(var(--bloque-card))] py-1 shadow-lg"
          role="menu"
        >
          <div className="border-b border-[hsl(var(--bloque-border))] px-3 py-2">
            {userProp.name && (
              <p className="text-sm font-medium text-[hsl(var(--bloque-foreground))]">
                {userProp.name}
              </p>
            )}
            {userProp.email && (
              <p className="text-xs text-[hsl(var(--bloque-muted-foreground))]">
                {userProp.email}
              </p>
            )}
            {!userProp.name && !userProp.email && (
              <p className="text-sm text-[hsl(var(--bloque-muted-foreground))]">
                {userProp.userId}
              </p>
            )}
          </div>
          {actions && (
            <div className="border-b border-[hsl(var(--bloque-border))] py-1">
              {actions}
            </div>
          )}
          {onLogout && (
            <div className="py-1">
              <button
                type="button"
                onClick={() => {
                  onLogout();
                  setOpen(false);
                }}
                className="flex w-full px-3 py-2 text-left text-sm text-[hsl(var(--bloque-destructive))] hover:bg-[hsl(var(--bloque-accent))]"
                role="menuitem"
              >
                Log out
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
