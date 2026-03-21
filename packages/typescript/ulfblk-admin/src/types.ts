/**
 * Configuration options for the ulfblk DataProvider.
 */
export interface DataProviderOptions {
  /** Base path for API endpoints. Default: "/api" */
  basePath?: string;

  /**
   * Custom query string serializer.
   * Default uses `qs` with arrayFormat: 'repeat' (FastAPI-compatible).
   */
  querySerializer?: (params: Record<string, unknown>) => string;
}

/**
 * Configuration options for the ulfblk AuthProvider.
 */
export interface AuthProviderOptions {
  /** Path for the login endpoint. Default: "/auth/login" */
  loginPath?: string;
}

/**
 * Expected response format from list endpoints.
 * Must match PaginatedResponse from the Python backend.
 */
export interface ListResponse<T = Record<string, unknown>> {
  items: T[];
  total: number;
  page?: number;
  page_size?: number;
  pages?: number;
}
