import type { RequestInterceptor, TokenStorage } from "../types.js";

/** Adds Authorization header from token storage */
export function createAuthInterceptor(
  tokenStorage: TokenStorage,
): RequestInterceptor {
  return (_url: string, init: RequestInit): RequestInit => {
    const token = tokenStorage.getAccessToken();
    if (token) {
      const headers = new Headers(init.headers);
      headers.set("Authorization", `Bearer ${token}`);
      return { ...init, headers };
    }
    return init;
  };
}
