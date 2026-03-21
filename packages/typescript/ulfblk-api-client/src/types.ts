/** Configuration for BloqueClient */
export interface ClientConfig {
  /** Base URL of the API (e.g. "https://api.example.com") */
  baseUrl: string;
  /** Default headers sent with every request */
  defaultHeaders?: Record<string, string>;
  /** Request timeout in milliseconds (default: 30000) */
  timeout?: number;
  /** Token storage implementation */
  tokenStorage?: TokenStorage;
}

/** Options for individual requests */
export interface RequestOptions {
  headers?: Record<string, string>;
  params?: Record<string, string>;
  signal?: AbortSignal;
  timeout?: number;
}

/** Request interceptor - modifies request before sending */
export interface RequestInterceptor {
  (url: string, init: RequestInit): RequestInit | Promise<RequestInit>;
}

/** Response interceptor - processes response before returning */
export interface ResponseInterceptor {
  (response: Response): Response | Promise<Response>;
}

/** Token storage interface for persistence */
export interface TokenStorage {
  getAccessToken(): string | null;
  getRefreshToken(): string | null;
  setTokens(accessToken: string, refreshToken: string): void;
  clear(): void;
}
