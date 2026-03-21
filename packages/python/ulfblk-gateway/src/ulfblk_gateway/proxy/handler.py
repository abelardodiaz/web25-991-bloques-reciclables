"""Proxy handler: forwards requests to upstream services via httpx."""

from __future__ import annotations

import httpx
from starlette.requests import Request

from ulfblk_gateway.proxy.settings import ProxyRoute, ProxySettings


class ProxyHandler:
    """Manages upstream connections and request forwarding.

    Example:
        handler = ProxyHandler(settings)
        await handler.start()
        route = handler.match_route("/api/users/123")
        if route:
            response = await handler.forward(request, route)
        await handler.stop()
    """

    def __init__(self, settings: ProxySettings) -> None:
        self.settings = settings
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        """Create the httpx.AsyncClient."""
        if self._client is not None:
            return
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                self.settings.default_timeout,
                connect=self.settings.connect_timeout,
            ),
            follow_redirects=False,
        )

    async def stop(self) -> None:
        """Close the httpx.AsyncClient."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the httpx client. Raises RuntimeError if not started."""
        if self._client is None:
            raise RuntimeError(
                "ProxyHandler is not started. Call start() or use async with."
            )
        return self._client

    def match_route(self, path: str) -> ProxyRoute | None:
        """Find the first matching route for a given path.

        Routes are matched in order; first match wins.
        """
        for route in self.settings.routes:
            if path.startswith(route.path_prefix):
                return route
        return None

    async def forward(
        self, request: Request, route: ProxyRoute
    ) -> httpx.Response:
        """Forward a request to the upstream service.

        Reads the full request body (no streaming in v0.1).
        """
        # Build upstream URL
        path = request.url.path
        if route.strip_prefix:
            path = path[len(route.path_prefix) :]
            if not path.startswith("/"):
                path = "/" + path

        upstream_url = route.upstream_url.rstrip("/") + path
        if request.url.query:
            upstream_url += f"?{request.url.query}"

        # Build headers (exclude hop-by-hop)
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("transfer-encoding", None)

        if self.settings.forward_headers and request.client:
            headers["X-Forwarded-For"] = request.client.host
            if hasattr(request.state, "request_id"):
                headers["X-Request-ID"] = request.state.request_id

        # Read body
        body = await request.body()

        # Forward with retries
        last_exc: Exception | None = None
        attempts = 1 + route.retries

        for _ in range(attempts):
            try:
                response = await self.client.request(
                    method=request.method,
                    url=upstream_url,
                    headers=headers,
                    content=body,
                    timeout=route.timeout,
                )
                return response
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                last_exc = exc

        raise last_exc  # type: ignore[misc]

    async def check_upstream(self, url: str) -> bool:
        """Health check an upstream URL. Returns True if reachable."""
        try:
            response = await self.client.get(url, timeout=5.0)
            return response.status_code < 500
        except Exception:
            return False

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
