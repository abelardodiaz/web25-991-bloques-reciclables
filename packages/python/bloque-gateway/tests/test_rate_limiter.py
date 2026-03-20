"""Tests for rate limiter middleware and backends."""

import pytest
from bloque_gateway.rate_limiter import (
    InMemoryBackend,
    RateLimiterMiddleware,
    RateLimiterSettings,
)
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


def create_rate_limited_app(
    settings: RateLimiterSettings | None = None,
    backend: InMemoryBackend | None = None,
) -> FastAPI:
    app = FastAPI()

    @app.get("/echo")
    async def echo():
        return {"message": "ok"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    app.add_middleware(
        RateLimiterMiddleware,
        settings=settings or RateLimiterSettings(requests=3, window_seconds=60),
        backend=backend or InMemoryBackend(),
    )
    return app


@pytest.mark.asyncio
async def test_allows_requests_within_limit():
    app = create_rate_limited_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for _ in range(3):
            response = await client.get("/echo")
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_blocks_requests_over_limit():
    app = create_rate_limited_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for _ in range(3):
            await client.get("/echo")
        response = await client.get("/echo")
        assert response.status_code == 429
        data = response.json()
        assert data["detail"] == "Rate limit exceeded"
        assert data["code"] == "RATE_LIMITED"


@pytest.mark.asyncio
async def test_rate_limit_headers():
    app = create_rate_limited_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/echo")
        assert response.status_code == 200
        assert response.headers["X-RateLimit-Limit"] == "3"
        assert response.headers["X-RateLimit-Remaining"] == "2"
        assert "X-RateLimit-Reset" in response.headers


@pytest.mark.asyncio
async def test_rate_limit_remaining_decreases():
    app = create_rate_limited_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r1 = await client.get("/echo")
        assert r1.headers["X-RateLimit-Remaining"] == "2"
        r2 = await client.get("/echo")
        assert r2.headers["X-RateLimit-Remaining"] == "1"
        r3 = await client.get("/echo")
        assert r3.headers["X-RateLimit-Remaining"] == "0"


@pytest.mark.asyncio
async def test_429_includes_headers():
    app = create_rate_limited_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for _ in range(3):
            await client.get("/echo")
        response = await client.get("/echo")
        assert response.status_code == 429
        assert response.headers["X-RateLimit-Remaining"] == "0"


@pytest.mark.asyncio
async def test_headers_disabled():
    settings = RateLimiterSettings(requests=3, window_seconds=60, headers_enabled=False)
    app = create_rate_limited_app(settings=settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/echo")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" not in response.headers


@pytest.mark.asyncio
async def test_excluded_paths_not_rate_limited():
    settings = RateLimiterSettings(
        requests=1, window_seconds=60, exclude_paths=["/health"]
    )
    app = create_rate_limited_app(settings=settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First request to /echo uses the 1 allowed request
        r1 = await client.get("/echo")
        assert r1.status_code == 200
        # Second request to /echo should be blocked
        r2 = await client.get("/echo")
        assert r2.status_code == 429
        # But /health should still work (excluded)
        r3 = await client.get("/health")
        assert r3.status_code == 200


@pytest.mark.asyncio
async def test_custom_key_func():
    def custom_key(request):
        return request.headers.get("X-API-Key", "anonymous")

    app = FastAPI()

    @app.get("/echo")
    async def echo():
        return {"message": "ok"}

    app.add_middleware(
        RateLimiterMiddleware,
        settings=RateLimiterSettings(requests=1, window_seconds=60),
        backend=InMemoryBackend(),
        key_func=custom_key,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Key "user-a" uses its 1 request
        r1 = await client.get("/echo", headers={"X-API-Key": "user-a"})
        assert r1.status_code == 200
        r2 = await client.get("/echo", headers={"X-API-Key": "user-a"})
        assert r2.status_code == 429
        # Key "user-b" has its own window
        r3 = await client.get("/echo", headers={"X-API-Key": "user-b"})
        assert r3.status_code == 200


@pytest.mark.asyncio
async def test_in_memory_backend_sliding_window():
    backend = InMemoryBackend()
    # Fill the window
    for _ in range(5):
        allowed, _, _ = await backend.is_allowed("test", 5, 60)
        assert allowed is True
    # 6th should fail
    allowed, remaining, _ = await backend.is_allowed("test", 5, 60)
    assert allowed is False
    assert remaining == 0


@pytest.mark.asyncio
async def test_different_paths_share_rate_limit():
    """Different paths from same client share the rate limit (keyed by IP)."""
    app = create_rate_limited_app(
        settings=RateLimiterSettings(requests=2, window_seconds=60)
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r1 = await client.get("/echo")
        assert r1.status_code == 200
        r2 = await client.get("/health")
        assert r2.status_code == 200
        r3 = await client.get("/echo")
        assert r3.status_code == 429
