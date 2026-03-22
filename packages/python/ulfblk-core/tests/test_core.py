"""Tests for ulfblk-core middleware, schemas, and health."""


import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from ulfblk_core.health import health_router
from ulfblk_core.middleware import RequestIDMiddleware, TimingMiddleware
from ulfblk_core.schemas import ErrorResponse, HealthResponse, PaginatedResponse


def create_test_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.include_router(health_router)

    @app.get("/echo")
    async def echo():
        return {"message": "ok"}

    return app


@pytest.fixture
def app():
    return create_test_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api"


@pytest.mark.asyncio
async def test_request_id_generated(client):
    response = await client.get("/echo")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) == 36  # UUID4 format


@pytest.mark.asyncio
async def test_request_id_propagated(client):
    custom_id = "test-request-123"
    response = await client.get("/echo", headers={"X-Request-ID": custom_id})
    assert response.headers["X-Request-ID"] == custom_id


@pytest.mark.asyncio
async def test_timing_header(client):
    response = await client.get("/echo")
    assert "X-Process-Time" in response.headers
    time_str = response.headers["X-Process-Time"]
    assert time_str.endswith("ms")


def test_paginated_response():
    items = [{"id": 1}, {"id": 2}]
    result = PaginatedResponse.create(items=items, total=50, page=1, page_size=20)
    assert result.total == 50
    assert result.pages == 3
    assert result.page == 1
    assert len(result.items) == 2


def test_health_response_healthy():
    h = HealthResponse.healthy(service="test", version="1.0.0")
    assert h.status == "healthy"
    assert h.service == "test"


def test_error_response():
    err = ErrorResponse(detail="Something went wrong", code="ERR_001")
    assert err.detail == "Something went wrong"
    assert err.code == "ERR_001"
