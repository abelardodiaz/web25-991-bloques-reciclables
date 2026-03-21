"""Tests for health router factory."""

import pytest
from ulfblk_core.health.router import create_health_router, health_router
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


def _make_app(router):
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.mark.asyncio
async def test_factory_defaults():
    app = _make_app(create_health_router())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "api"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_factory_custom():
    router = create_health_router(service_name="billing", version="3.0.0")
    app = _make_app(router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    data = resp.json()
    assert data["service"] == "billing"
    assert data["version"] == "3.0.0"


@pytest.mark.asyncio
async def test_backwards_compat_instance():
    """The module-level health_router still works."""
    app = _make_app(health_router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "api"


def test_router_tag():
    router = create_health_router()
    # All routes should have the "health" tag
    for route in router.routes:
        if hasattr(route, "tags"):
            assert "health" in route.tags
