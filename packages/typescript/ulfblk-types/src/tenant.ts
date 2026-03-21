import type { BaseEntity } from "./entity.js";

/** Tenant entity */
export interface Tenant extends BaseEntity {
  slug: string;
  name: string;
  isActive: boolean;
}

/** Current tenant context for request scoping */
export interface TenantContext {
  tenantId: string;
  tenantSlug?: string;
  tenantName?: string;
}

/** Tenant-level configuration */
export interface TenantConfig {
  tenantId: string;
  features: Record<string, boolean>;
  settings: Record<string, unknown>;
}
