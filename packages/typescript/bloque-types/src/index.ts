/**
 * @bloque/types - Base TypeScript types for the Bloque ecosystem.
 */

/** Paginated API response */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

/** Standard error response */
export interface ErrorResponse {
  detail: string;
  code?: string;
  errors?: Record<string, unknown>[];
}

/** Health check response */
export interface HealthResponse {
  status: "healthy" | "degraded" | "unhealthy";
  service: string;
  version: string;
  timestamp: string;
  checks?: Record<string, boolean>;
}

/** Auth token data */
export interface TokenData {
  user_id: string;
  tenant_id: string;
  roles: string[];
  permissions: string[];
  token_type: "access" | "refresh";
}

/** Base entity with common fields */
export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string;
}
