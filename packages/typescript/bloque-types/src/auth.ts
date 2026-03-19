import type { BaseEntity } from "./entity.js";

/** Login request payload */
export interface LoginRequest {
  email: string;
  password: string;
}

/** Login response from the server */
export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
}

/** Pair of JWT tokens */
export interface TokenPair {
  accessToken: string;
  refreshToken: string;
}

/** Decoded JWT token payload (mirrors bloque_auth/jwt/manager.py:TokenPayload) */
export interface TokenPayload {
  sub: string;
  tenantId: string;
  roles: string[];
  permissions: string[];
  tokenType: "access" | "refresh";
  exp: number;
  iat: number;
}

/** Auth token data for runtime use */
export interface TokenData {
  userId: string;
  tenantId: string;
  roles: string[];
  permissions: string[];
  tokenType: "access" | "refresh";
}

/** User entity */
export interface User extends BaseEntity {
  email: string;
  tenantId: string;
  roles: string[];
  isActive: boolean;
}

/** State of a login attempt for brute force tracking */
export interface LoginAttemptState {
  attempts: number;
  lastAttempt: string | null;
  lockedUntil: string | null;
}
