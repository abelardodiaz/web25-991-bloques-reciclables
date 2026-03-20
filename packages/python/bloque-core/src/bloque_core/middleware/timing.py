"""Timing middleware for request duration measurement."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that measures request processing time.
    Adds X-Process-Time header to the response.
    """

    def __init__(self, app, slow_request_threshold: float = 1.0) -> None:
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        process_time_ms = round(process_time * 1000, 2)

        response.headers["X-Process-Time"] = f"{process_time_ms}ms"

        if process_time > self.slow_request_threshold:
            logger.warning(
                "Slow request: path=%s method=%s duration_ms=%s",
                request.url.path,
                request.method,
                process_time_ms,
            )

        return response
