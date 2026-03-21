/**
 * React Admin AuthProvider using BloqueClient.
 *
 * Handles login/logout, token validation via jwt-decode,
 * and permission extraction from JWT payload.
 */

import type { AuthProvider } from "react-admin";
import type { BloqueClient } from "@ulfblk/api-client";
import { jwtDecode } from "jwt-decode";
import type { AuthProviderOptions } from "./types.js";

interface JwtPayload {
  sub: string;
  tenant: string;
  exp: number;
  type: string;
  roles?: string[];
  permissions?: string[];
}

function isTokenExpired(token: string): boolean {
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    return decoded.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

function getPayload(token: string): JwtPayload | null {
  try {
    return jwtDecode<JwtPayload>(token);
  } catch {
    return null;
  }
}

export function createAuthProvider(
  client: BloqueClient,
  options?: AuthProviderOptions,
): AuthProvider {
  const loginPath = options?.loginPath ?? "/auth/login";
  let lastToken: string | null = null;

  return {
    login: async ({ username, password }: { username: string; password: string }) => {
      const response = await client.post<{ access_token: string; refresh_token: string }>(
        loginPath,
        { email: username, password },
      );
      client.setTokens({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
      });
      lastToken = response.access_token;
    },

    logout: async () => {
      client.logout();
      lastToken = null;
    },

    checkAuth: async () => {
      if (!lastToken || isTokenExpired(lastToken)) {
        throw new Error("Token expired or missing");
      }
    },

    checkError: async (error: { status?: number }) => {
      if (error.status === 401) {
        client.logout();
        lastToken = null;
        throw new Error("Unauthorized");
      }
      // 403 = valid token but no permission - don't logout
      if (error.status === 403) {
        throw new Error("Forbidden");
      }
    },

    getPermissions: async () => {
      if (!lastToken) return { roles: [], permissions: [] };
      const payload = getPayload(lastToken);
      if (!payload) return { roles: [], permissions: [] };
      return {
        roles: payload.roles ?? [],
        permissions: payload.permissions ?? [],
      };
    },

    getIdentity: async () => {
      if (!lastToken) throw new Error("Not authenticated");
      const payload = getPayload(lastToken);
      if (!payload) throw new Error("Invalid token");
      return {
        id: payload.sub,
        fullName: payload.sub,
        tenant: payload.tenant,
      };
    },
  };
}
