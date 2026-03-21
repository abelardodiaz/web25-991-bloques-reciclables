import type { ReactNode } from "react";
import { useAuth } from "../hooks/use-auth.js";

export interface RequireRoleProps {
  roles: string[];
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Renders children if the user has ANY of the specified roles.
 * Mirrors Python's require_roles (intersection check).
 */
export function RequireRole({ roles, children, fallback = null }: RequireRoleProps) {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return <>{fallback}</>;
  }

  const userRoles = new Set(user.roles);
  const hasRole = roles.some((role) => userRoles.has(role));

  if (!hasRole) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
