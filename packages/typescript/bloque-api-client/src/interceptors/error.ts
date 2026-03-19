import type { ErrorResponse } from "@bloque/types";
import type { ResponseInterceptor } from "../types.js";

/** Error thrown by BloqueClient with normalized error info */
export class BloqueApiError extends Error {
  public readonly status: number;
  public readonly errorResponse: ErrorResponse;

  constructor(status: number, errorResponse: ErrorResponse) {
    super(errorResponse.detail);
    this.name = "BloqueApiError";
    this.status = status;
    this.errorResponse = errorResponse;
  }
}

/** Normalizes non-OK responses to BloqueApiError */
export function createErrorInterceptor(): ResponseInterceptor {
  return async (response: Response): Promise<Response> => {
    if (response.ok) {
      return response;
    }

    let errorResponse: ErrorResponse;
    try {
      errorResponse = (await response.clone().json()) as ErrorResponse;
    } catch {
      errorResponse = {
        detail: response.statusText || `HTTP ${response.status}`,
        code: `HTTP_${response.status}`,
      };
    }

    throw new BloqueApiError(response.status, errorResponse);
  };
}
