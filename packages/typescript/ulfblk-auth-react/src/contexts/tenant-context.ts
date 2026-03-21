import { createContext, useContext, useState, useEffect, useCallback, createElement } from "react";
import type { ReactNode } from "react";
import type { TenantContext as TenantContextType } from "@ulfblk/types";
import { useBloqueContext } from "./bloque-context.js";
import { useAuthContext } from "./auth-context.js";

export interface TenantContextValue {
  tenantId: string | null;
  setTenantId: (id: string) => void;
  tenantContext: TenantContextType | null;
}

const TenantContext = createContext<TenantContextValue | null>(null);

export interface TenantProviderProps {
  children: ReactNode;
}

export function TenantProvider({ children }: TenantProviderProps) {
  const client = useBloqueContext();
  const { user } = useAuthContext();
  const [tenantId, setTenantIdState] = useState<string | null>(user?.tenantId ?? null);

  // Sync tenant from user token
  useEffect(() => {
    if (user?.tenantId) {
      setTenantIdState(user.tenantId);
      client.setTenantId(user.tenantId);
    }
  }, [user?.tenantId, client]);

  const setTenantId = useCallback(
    (id: string) => {
      setTenantIdState(id);
      client.setTenantId(id);
    },
    [client],
  );

  const tenantContext: TenantContextType | null = tenantId ? { tenantId } : null;

  const value: TenantContextValue = {
    tenantId,
    setTenantId,
    tenantContext,
  };

  return createElement(TenantContext.Provider, { value }, children);
}

export function useTenantContext(): TenantContextValue {
  const ctx = useContext(TenantContext);
  if (!ctx) {
    throw new Error("useTenantContext must be used within a TenantProvider");
  }
  return ctx;
}
