/**
 * @bloque/api-client - HTTP API client for the Bloque ecosystem.
 * Zero external dependencies. Uses native fetch (browser + Node 18+ + Deno + Bun).
 */

export { BloqueClient } from "./client.js";
export { BloqueApiError } from "./interceptors/error.js";
export { MemoryTokenStorage, LocalStorageTokenStorage } from "./token-storage.js";
export { createAuthInterceptor } from "./interceptors/auth.js";
export { createTenantInterceptor } from "./interceptors/tenant.js";
export { createErrorInterceptor } from "./interceptors/error.js";

export type {
  ClientConfig,
  RequestOptions,
  RequestInterceptor,
  ResponseInterceptor,
  TokenStorage,
} from "./types.js";
