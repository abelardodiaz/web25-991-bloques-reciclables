import type { LoginRequest, LoginResponse, TokenPair } from "@bloque/types";
import type {
  ClientConfig,
  RequestInterceptor,
  RequestOptions,
  ResponseInterceptor,
  TokenStorage,
} from "./types.js";
import { createAuthInterceptor } from "./interceptors/auth.js";
import { createTenantInterceptor } from "./interceptors/tenant.js";
import { createErrorInterceptor } from "./interceptors/error.js";
import { MemoryTokenStorage } from "./token-storage.js";

const DEFAULT_TIMEOUT = 30_000;

/** HTTP API client for the Bloque ecosystem */
export class BloqueClient {
  private readonly baseUrl: string;
  private readonly defaultHeaders: Record<string, string>;
  private readonly timeout: number;
  private readonly tokenStorage: TokenStorage;
  private tenantId: string | null = null;

  private readonly requestInterceptors: RequestInterceptor[] = [];
  private readonly responseInterceptors: ResponseInterceptor[] = [];

  constructor(config: ClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/+$/, "");
    this.defaultHeaders = config.defaultHeaders ?? {};
    this.timeout = config.timeout ?? DEFAULT_TIMEOUT;
    this.tokenStorage = config.tokenStorage ?? new MemoryTokenStorage();

    // Register default interceptors
    this.requestInterceptors.push(
      createAuthInterceptor(this.tokenStorage),
      createTenantInterceptor(() => this.tenantId),
    );
    this.responseInterceptors.push(createErrorInterceptor());
  }

  /** Add a custom request interceptor */
  addRequestInterceptor(interceptor: RequestInterceptor): void {
    this.requestInterceptors.push(interceptor);
  }

  /** Add a custom response interceptor */
  addResponseInterceptor(interceptor: ResponseInterceptor): void {
    this.responseInterceptors.push(interceptor);
  }

  /** Set the active tenant ID for subsequent requests */
  setTenantId(id: string): void {
    this.tenantId = id;
  }

  /** Store tokens in the configured token storage */
  setTokens(tokens: TokenPair): void {
    this.tokenStorage.setTokens(tokens.accessToken, tokens.refreshToken);
  }

  /** Login and store tokens */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.post<LoginResponse>(
      "/auth/login",
      credentials,
    );
    this.tokenStorage.setTokens(response.accessToken, response.refreshToken);
    return response;
  }

  /** Clear stored tokens */
  logout(): void {
    this.tokenStorage.clear();
  }

  async get<T>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>("GET", path, undefined, options);
  }

  async post<T>(
    path: string,
    body?: unknown,
    options?: RequestOptions,
  ): Promise<T> {
    return this.request<T>("POST", path, body, options);
  }

  async put<T>(
    path: string,
    body?: unknown,
    options?: RequestOptions,
  ): Promise<T> {
    return this.request<T>("PUT", path, body, options);
  }

  async patch<T>(
    path: string,
    body?: unknown,
    options?: RequestOptions,
  ): Promise<T> {
    return this.request<T>("PATCH", path, body, options);
  }

  async delete<T>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>("DELETE", path, undefined, options);
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
    options?: RequestOptions,
  ): Promise<T> {
    let url = `${this.baseUrl}${path}`;

    if (options?.params) {
      const search = new URLSearchParams(options.params);
      url += `?${search.toString()}`;
    }

    const headers = new Headers({
      "Content-Type": "application/json",
      ...this.defaultHeaders,
      ...options?.headers,
    });

    let init: RequestInit = {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    };

    // Apply request interceptors
    for (const interceptor of this.requestInterceptors) {
      init = await interceptor(url, init);
    }

    // Timeout via AbortSignal
    const timeoutMs = options?.timeout ?? this.timeout;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    if (options?.signal) {
      options.signal.addEventListener("abort", () => controller.abort());
    }

    try {
      let response = await fetch(url, {
        ...init,
        signal: controller.signal,
      });

      // Apply response interceptors
      for (const interceptor of this.responseInterceptors) {
        response = await interceptor(response);
      }

      // 204 No Content
      if (response.status === 204) {
        return undefined as T;
      }

      return (await response.json()) as T;
    } finally {
      clearTimeout(timeoutId);
    }
  }
}
