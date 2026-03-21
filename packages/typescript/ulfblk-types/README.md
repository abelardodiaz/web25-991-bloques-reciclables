# @bloque/types

Base TypeScript types for the Bloque ecosystem. Mirrors the data models from the Python backend (`bloque-core`, `bloque-auth`, `bloque-multitenant`).

## Install

```bash
pnpm add @bloque/types
```

## Types

### Entity

```typescript
import type { BaseEntity, SoftDeletableEntity, AuditableEntity } from "@bloque/types";
```

| Type | Description |
|------|-------------|
| `BaseEntity` | `id`, `createdAt`, `updatedAt` |
| `SoftDeletableEntity` | BaseEntity + `deletedAt` |
| `AuditableEntity` | BaseEntity + `createdBy`, `updatedBy` |

### API

```typescript
import type { PaginatedResponse, ErrorResponse, SuccessResponse, HealthResponse } from "@bloque/types";
```

| Type | Description |
|------|-------------|
| `PaginatedResponse<T>` | `items`, `total`, `page`, `pageSize`, `pages` |
| `ErrorResponse` | `detail`, `code?`, `errors?` |
| `SuccessResponse<T>` | `data`, `message?` |
| `HealthResponse` | `status`, `service`, `version`, `timestamp`, `checks?` |

### Auth

```typescript
import type { LoginRequest, LoginResponse, TokenPair, TokenPayload, TokenData, User, LoginAttemptState } from "@bloque/types";
```

| Type | Description |
|------|-------------|
| `LoginRequest` | `email`, `password` |
| `LoginResponse` | `accessToken`, `refreshToken`, `tokenType` |
| `TokenPair` | `accessToken`, `refreshToken` |
| `TokenPayload` | JWT claims: `sub`, `tenantId`, `roles`, `permissions`, `tokenType`, `exp`, `iat` |
| `TokenData` | Runtime: `userId`, `tenantId`, `roles`, `permissions`, `tokenType` |
| `User` | BaseEntity + `email`, `tenantId`, `roles`, `isActive` |
| `LoginAttemptState` | Brute force: `attempts`, `lastAttempt`, `lockedUntil` |

### Tenant

```typescript
import type { Tenant, TenantContext, TenantConfig } from "@bloque/types";
```

| Type | Description |
|------|-------------|
| `Tenant` | BaseEntity + `slug`, `name`, `isActive` |
| `TenantContext` | `tenantId`, `tenantSlug?`, `tenantName?` |
| `TenantConfig` | `tenantId`, `features`, `settings` |

## License

MIT
