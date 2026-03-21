/**
 * @ulfblk/types - Base TypeScript types for the Bloque ecosystem.
 */

export type {
  BaseEntity,
  SoftDeletableEntity,
  AuditableEntity,
} from "./entity.js";

export type {
  PaginatedResponse,
  ErrorResponse,
  SuccessResponse,
  HealthResponse,
} from "./api.js";

export type {
  LoginRequest,
  LoginResponse,
  TokenPair,
  TokenPayload,
  TokenData,
  User,
  LoginAttemptState,
} from "./auth.js";

export type {
  Tenant,
  TenantContext,
  TenantConfig,
} from "./tenant.js";
