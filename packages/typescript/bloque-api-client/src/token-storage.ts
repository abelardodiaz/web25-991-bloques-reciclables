import type { TokenStorage } from "./types.js";

/** In-memory token storage (works everywhere, lost on page refresh) */
export class MemoryTokenStorage implements TokenStorage {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  getAccessToken(): string | null {
    return this.accessToken;
  }

  getRefreshToken(): string | null {
    return this.refreshToken;
  }

  setTokens(accessToken: string, refreshToken: string): void {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
  }

  clear(): void {
    this.accessToken = null;
    this.refreshToken = null;
  }
}

/** localStorage-based token storage (browser only) */
export class LocalStorageTokenStorage implements TokenStorage {
  private readonly accessTokenKey: string;
  private readonly refreshTokenKey: string;

  constructor(prefix = "bloque") {
    this.accessTokenKey = `${prefix}_access_token`;
    this.refreshTokenKey = `${prefix}_refresh_token`;
  }

  getAccessToken(): string | null {
    return globalThis.localStorage?.getItem(this.accessTokenKey) ?? null;
  }

  getRefreshToken(): string | null {
    return globalThis.localStorage?.getItem(this.refreshTokenKey) ?? null;
  }

  setTokens(accessToken: string, refreshToken: string): void {
    globalThis.localStorage?.setItem(this.accessTokenKey, accessToken);
    globalThis.localStorage?.setItem(this.refreshTokenKey, refreshToken);
  }

  clear(): void {
    globalThis.localStorage?.removeItem(this.accessTokenKey);
    globalThis.localStorage?.removeItem(this.refreshTokenKey);
  }
}
