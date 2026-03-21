import type { RequestInterceptor } from "../types.js";

/** Adds X-Tenant-ID header to requests */
export function createTenantInterceptor(
  getTenantId: () => string | null,
): RequestInterceptor {
  return (_url: string, init: RequestInit): RequestInit => {
    const tenantId = getTenantId();
    if (tenantId) {
      const headers = new Headers(init.headers);
      headers.set("X-Tenant-ID", tenantId);
      return { ...init, headers };
    }
    return init;
  };
}
