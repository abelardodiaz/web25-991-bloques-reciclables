"""Tests for proxy handler and middleware."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from ulfblk_gateway.circuit_breaker import CircuitBreaker, CircuitBreakerSettings
from ulfblk_gateway.proxy import (
    ProxyHandler,
    ProxyMiddleware,
    ProxyRoute,
    ProxySettings,
)
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def single_route_settings():
    return ProxySettings(
        routes=[
            ProxyRoute(
                path_prefix="/api/users",
                upstream_url="http://user-service:8001",
            ),
        ]
    )


def test_match_route(proxy_handler):
    route = proxy_handler.match_route("/api/users/123")
    assert route is not None
    assert route.upstream_url == "http://user-service:8001"


def test_match_route_no_match(proxy_handler):
    route = proxy_handler.match_route("/api/products/1")
    assert route is None


def test_match_route_order(proxy_handler):
    """First matching route wins."""
    route = proxy_handler.match_route("/api/orders/42")
    assert route is not None
    assert route.upstream_url == "http://order-service:8002"


@pytest.mark.asyncio
async def test_handler_not_started():
    handler = ProxyHandler(ProxySettings())
    with pytest.raises(RuntimeError, match="not started"):
        _ = handler.client


@pytest.mark.asyncio
async def test_handler_start_stop():
    handler = ProxyHandler(ProxySettings())
    await handler.start()
    assert handler.client is not None
    await handler.stop()
    with pytest.raises(RuntimeError):
        _ = handler.client


@pytest.mark.asyncio
async def test_forward_strips_prefix():
    settings = ProxySettings(
        routes=[ProxyRoute(path_prefix="/api/users", upstream_url="http://svc:8001")]
    )
    handler = ProxyHandler(settings)
    await handler.start()

    mock_response = httpx.Response(200, json={"id": 1, "name": "Alice"})

    with patch.object(handler.client, "request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response

        from starlette.requests import Request

        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/api/users/123",
                "query_string": b"",
                "headers": [(b"host", b"test")],
            }
        )
        request._body = b""

        route = handler.match_route("/api/users/123")
        response = await handler.forward(request, route)

        call_kwargs = mock_req.call_args
        assert "/123" in call_kwargs.kwargs["url"]
        assert response.status_code == 200

    await handler.stop()


@pytest.mark.asyncio
async def test_forward_keeps_prefix_when_strip_false():
    settings = ProxySettings(
        routes=[
            ProxyRoute(
                path_prefix="/api/orders",
                upstream_url="http://svc:8002",
                strip_prefix=False,
            )
        ]
    )
    handler = ProxyHandler(settings)
    await handler.start()

    mock_response = httpx.Response(200, json={"order": 1})

    with patch.object(handler.client, "request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response

        from starlette.requests import Request

        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/api/orders/42",
                "query_string": b"",
                "headers": [(b"host", b"test")],
            }
        )
        request._body = b""

        route = handler.match_route("/api/orders/42")
        await handler.forward(request, route)

        call_kwargs = mock_req.call_args
        assert "/api/orders/42" in call_kwargs.kwargs["url"]

    await handler.stop()


@pytest.mark.asyncio
async def test_proxy_middleware_passes_unmatched():
    """Non-matching paths pass through to local app."""
    app = FastAPI()

    @app.get("/local")
    async def local():
        return {"source": "local"}

    handler = ProxyHandler(
        ProxySettings(
            routes=[ProxyRoute(path_prefix="/api/remote", upstream_url="http://svc:9000")]
        )
    )
    await handler.start()

    app.add_middleware(ProxyMiddleware, handler=handler)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/local")
        assert response.status_code == 200
        assert response.json()["source"] == "local"

    await handler.stop()


@pytest.mark.asyncio
async def test_proxy_middleware_returns_502_on_failure():
    """Upstream connection failure returns 502."""
    app = FastAPI()

    @app.get("/echo")
    async def echo():
        return {"message": "ok"}

    handler = ProxyHandler(
        ProxySettings(
            routes=[ProxyRoute(path_prefix="/api/fail", upstream_url="http://svc:9999")]
        )
    )
    await handler.start()

    with patch.object(
        handler.client,
        "request",
        new_callable=AsyncMock,
        side_effect=httpx.ConnectError("Connection refused"),
    ):
        app.add_middleware(ProxyMiddleware, handler=handler)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/fail/test")
            assert response.status_code == 502
            assert response.json()["code"] == "UPSTREAM_ERROR"

    await handler.stop()


@pytest.mark.asyncio
async def test_proxy_middleware_circuit_breaker_503():
    """Returns 503 when circuit breaker is open."""
    app = FastAPI()

    @app.get("/echo")
    async def echo():
        return {"message": "ok"}

    handler = ProxyHandler(
        ProxySettings(
            routes=[ProxyRoute(path_prefix="/api/svc", upstream_url="http://svc:8001")]
        )
    )
    await handler.start()

    cb = CircuitBreaker("svc", CircuitBreakerSettings(failure_threshold=1))
    cb.record_failure()  # Opens circuit immediately

    app.add_middleware(
        ProxyMiddleware,
        handler=handler,
        circuit_breakers={"http://svc:8001": cb},
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/svc/test")
        assert response.status_code == 503
        assert response.json()["code"] == "CIRCUIT_OPEN"

    await handler.stop()


@pytest.mark.asyncio
async def test_check_upstream_healthy():
    handler = ProxyHandler(ProxySettings())
    await handler.start()

    with patch.object(
        handler.client,
        "get",
        new_callable=AsyncMock,
        return_value=httpx.Response(200),
    ):
        result = await handler.check_upstream("http://svc:8001")
        assert result is True

    await handler.stop()


@pytest.mark.asyncio
async def test_check_upstream_unhealthy():
    handler = ProxyHandler(ProxySettings())
    await handler.start()

    with patch.object(
        handler.client,
        "get",
        new_callable=AsyncMock,
        side_effect=httpx.ConnectError("refused"),
    ):
        result = await handler.check_upstream("http://svc:8001")
        assert result is False

    await handler.stop()
