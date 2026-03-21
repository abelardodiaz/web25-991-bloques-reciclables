"""Rate limiter ASGI middleware."""

from __future__ import annotations

from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from ulfblk_gateway.rate_limiter.backends import RateLimiterBackend
from ulfblk_gateway.rate_limiter.settings import RateLimiterSettings


def _default_key_func(request: Request) -> str:
    """Extract client IP as default rate limit key."""
    if request.client:
        return request.client.host
    return "unknown"


def _resolve_tenant() -> str | None:
    """Try to read tenant from ulfblk_multitenant context (soft import)."""
    try:
        from ulfblk_multitenant.context import get_current_tenant

        ctx = get_current_tenant()
        return ctx.tenant_id if ctx else None
    except ImportError:
        return None


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that enforces sliding window rate limits.

    Returns 429 with JSON body when limit is exceeded.
    Adds X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers.

    Example:
        app.add_middleware(
            RateLimiterMiddleware,
            settings=RateLimiterSettings(requests=10, window_seconds=60),
            backend=InMemoryBackend(),
        )
    """

    def __init__(
        self,
        app,
        settings: RateLimiterSettings,
        backend: RateLimiterBackend,
        key_func: Callable[[Request], str] | None = None,
    ) -> None:
        super().__init__(app)
        self.settings = settings
        self.backend = backend
        self.key_func = key_func or _default_key_func

    async def dispatch(self, request: Request, call_next) -> Response:
        # Check excluded paths
        for excluded in self.settings.exclude_paths:
            if request.url.path.startswith(excluded):
                return await call_next(request)

        # Build rate limit key
        base_key = self.key_func(request)
        parts = [self.settings.key_prefix, base_key]

        if self.settings.tenant_aware:
            tenant_id = _resolve_tenant()
            if tenant_id:
                parts.insert(1, tenant_id)

        key = ":".join(parts)

        allowed, remaining, reset_at = await self.backend.is_allowed(
            key, self.settings.requests, self.settings.window_seconds
        )

        if not allowed:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "code": "RATE_LIMITED",
                },
            )
            if self.settings.headers_enabled:
                response.headers["X-RateLimit-Limit"] = str(self.settings.requests)
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(reset_at)
            return response

        response = await call_next(request)

        if self.settings.headers_enabled:
            response.headers["X-RateLimit-Limit"] = str(self.settings.requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_at)

        return response
