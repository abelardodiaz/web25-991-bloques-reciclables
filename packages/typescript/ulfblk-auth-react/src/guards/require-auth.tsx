import type { ReactNode } from "react";
import { useAuth } from "../hooks/use-auth.js";

export interface RequireAuthProps {
  children: ReactNode;
  fallback?: ReactNode;
  loadingFallback?: ReactNode;
}

/** Renders children only if the user is authenticated */
export function RequireAuth({ children, fallback = null, loadingFallback = null }: RequireAuthProps) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <>{loadingFallback}</>;
  }

  if (!isAuthenticated) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
