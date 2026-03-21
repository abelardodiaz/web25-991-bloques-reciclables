/** Paginated API response */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  pages: number;
}

/** Standard error response */
export interface ErrorResponse {
  detail: string;
  code?: string;
  errors?: Record<string, unknown>[];
}

/** Standard success response */
export interface SuccessResponse<T = unknown> {
  data: T;
  message?: string;
}

/** Health check response */
export interface HealthResponse {
  status: "healthy" | "degraded" | "unhealthy";
  service: string;
  version: string;
  timestamp: string;
  checks?: Record<string, boolean>;
}
