// JWT utilities
export { decodeToken, isTokenExpired } from "./jwt-decode.js";

// Providers
export { BloqueProvider } from "./contexts/bloque-context.js";
export type { BloqueProviderProps } from "./contexts/bloque-context.js";
export { AuthProvider } from "./contexts/auth-context.js";
export type { AuthProviderProps, AuthState } from "./contexts/auth-context.js";
export { TenantProvider } from "./contexts/tenant-context.js";
export type { TenantProviderProps } from "./contexts/tenant-context.js";

// Hooks
export { useBloqueClient } from "./hooks/use-bloque-client.js";
export { useAuth } from "./hooks/use-auth.js";
export type { UseAuthReturn } from "./hooks/use-auth.js";
export { useLogin } from "./hooks/use-login.js";
export type { UseLoginReturn } from "./hooks/use-login.js";
export { useLogout } from "./hooks/use-logout.js";
export type { UseLogoutReturn } from "./hooks/use-logout.js";
export { useTenant } from "./hooks/use-tenant.js";
export type { UseTenantReturn } from "./hooks/use-tenant.js";

// Guards
export { RequireAuth } from "./guards/require-auth.js";
export type { RequireAuthProps } from "./guards/require-auth.js";
export { RequireRole } from "./guards/require-role.js";
export type { RequireRoleProps } from "./guards/require-role.js";
export { RequirePermission } from "./guards/require-permission.js";
export type { RequirePermissionProps } from "./guards/require-permission.js";
