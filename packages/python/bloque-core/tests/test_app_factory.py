"""Tests for create_app factory."""

import pytest
from bloque_core.app import create_app
from bloque_core.config.settings import BloqueSettings
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_defaults(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "api"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_endpoint_present(client):
    resp = await client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_request_id_header(client):
    resp = await client.get("/health")
    assert "X-Request-ID" in resp.headers


@pytest.mark.asyncio
async def test_process_time_header(client):
    resp = await client.get("/health")
    assert "X-Process-Time" in resp.headers
    assert resp.headers["X-Process-Time"].endswith("ms")


@pytest.mark.asyncio
async def test_with_settings():
    settings = BloqueSettings(service_name="billing", version="5.0.0")
    app = create_app(settings=settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    data = resp.json()
    assert data["service"] == "billing"
    assert data["version"] == "5.0.0"


@pytest.mark.asyncio
async def test_settings_override_args():
    """Settings should take precedence over positional args."""
    settings = BloqueSettings(service_name="override", version="9.9.9")
    app = create_app(service_name="ignored", version="0.0.0", settings=settings)
    assert app.title == "override"
    assert app.version == "9.9.9"


@pytest.mark.asyncio
async def test_fastapi_kwargs():
    app = create_app(title="Custom Title", docs_url="/api-docs")
    assert app.title == "Custom Title"
    assert app.docs_url == "/api-docs"
