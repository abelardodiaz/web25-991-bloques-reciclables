import { useTenantContext } from "../contexts/tenant-context.js";
import type { TenantContext } from "@ulfblk/types";

export interface UseTenantReturn {
  tenantId: string | null;
  setTenantId: (id: string) => void;
  tenantContext: TenantContext | null;
}

/** Returns the current tenant context and a setter */
export function useTenant(): UseTenantReturn {
  return useTenantContext();
}
