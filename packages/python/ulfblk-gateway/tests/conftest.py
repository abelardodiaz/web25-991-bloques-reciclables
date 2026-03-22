"""Shared fixtures for ulfblk-gateway tests."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from ulfblk_gateway.circuit_breaker import CircuitBreaker, CircuitBreakerSettings
from ulfblk_gateway.proxy import ProxyHandler, ProxyRoute, ProxySettings
from ulfblk_gateway.rate_limiter import InMemoryBackend, RateLimiterSettings


def create_test_app() -> FastAPI:
    """Create a minimal FastAPI app for middleware testing."""
    app = FastAPI()

    @app.get("/echo")
    async def echo():
        return {"message": "ok"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


@pytest.fixture
def test_app():
    return create_test_app()


@pytest.fixture
def memory_backend():
    return InMemoryBackend()


@pytest.fixture
def rate_limiter_settings():
    return RateLimiterSettings(requests=3, window_seconds=60)


@pytest.fixture
def circuit_breaker():
    settings = CircuitBreakerSettings(
        failure_threshold=3,
        recovery_timeout=1.0,
        success_threshold=2,
    )
    return CircuitBreaker("test-service", settings)


@pytest.fixture
def proxy_settings():
    return ProxySettings(
        routes=[
            ProxyRoute(
                path_prefix="/api/users",
                upstream_url="http://user-service:8001",
            ),
            ProxyRoute(
                path_prefix="/api/orders",
                upstream_url="http://order-service:8002",
                strip_prefix=False,
            ),
        ],
        default_timeout=10.0,
    )


@pytest.fixture
def proxy_handler(proxy_settings):
    return ProxyHandler(proxy_settings)


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
