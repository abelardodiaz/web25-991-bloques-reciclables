import type { ReactNode } from "react";
import { useAuth } from "../hooks/use-auth.js";

export interface RequirePermissionProps {
  permissions: string[];
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Renders children if the user has ALL the specified permissions.
 * Admin bypass: users with "admin" role always pass.
 * Mirrors Python's require_permissions (set difference check + admin bypass).
 */
export function RequirePermission({ permissions, children, fallback = null }: RequirePermissionProps) {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return <>{fallback}</>;
  }

  // Admin bypass
  if (user.roles.includes("admin")) {
    return <>{children}</>;
  }

  const userPerms = new Set(user.permissions);
  const hasAll = permissions.every((perm) => userPerms.has(perm));

  if (!hasAll) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
