"""Proxy ASGI middleware."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from bloque_gateway.circuit_breaker.breaker import CircuitBreaker
from bloque_gateway.proxy.handler import ProxyHandler


class ProxyMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that forwards matching requests to upstream services.

    Non-matching paths pass through to the local app.
    Integrates with CircuitBreaker per upstream to prevent cascading failures.

    Returns:
        502 on upstream connection failure.
        503 when circuit breaker is open.

    Example:
        handler = ProxyHandler(settings)
        app.add_middleware(
            ProxyMiddleware,
            handler=handler,
            circuit_breakers={"http://svc:8001": CircuitBreaker("svc")},
        )
    """

    def __init__(
        self,
        app,
        handler: ProxyHandler,
        circuit_breakers: dict[str, CircuitBreaker] | None = None,
    ) -> None:
        super().__init__(app)
        self.handler = handler
        self.circuit_breakers = circuit_breakers or {}

    async def dispatch(self, request: Request, call_next) -> Response:
        route = self.handler.match_route(request.url.path)

        if route is None:
            return await call_next(request)

        # Check circuit breaker
        cb = self.circuit_breakers.get(route.upstream_url)
        if cb and not cb.allow_request():
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Service temporarily unavailable",
                    "code": "CIRCUIT_OPEN",
                },
            )

        try:
            upstream_response = await self.handler.forward(request, route)

            if cb:
                if upstream_response.status_code >= 500:
                    cb.record_failure()
                else:
                    cb.record_success()

            # Convert httpx.Response to Starlette Response
            return Response(
                content=upstream_response.content,
                status_code=upstream_response.status_code,
                headers=dict(upstream_response.headers),
            )
        except Exception:
            if cb:
                cb.record_failure()
            return JSONResponse(
                status_code=502,
                content={
                    "detail": "Bad gateway",
                    "code": "UPSTREAM_ERROR",
                },
            )
