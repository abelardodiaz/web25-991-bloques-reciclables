"""Tests for global exception handlers."""

import pytest
from bloque_core.exceptions.handlers import register_exception_handlers
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel


def _make_app():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/ok")
    async def ok():
        return {"status": "ok"}

    @app.get("/not-found")
    async def not_found():
        from starlette.exceptions import HTTPException
        raise HTTPException(status_code=404, detail="Resource not found")

    class Item(BaseModel):
        name: str
        price: float

    @app.post("/validate")
    async def validate(item: Item):
        return item.model_dump()

    @app.get("/crash")
    async def crash():
        raise RuntimeError("unexpected failure")

    # Disable Starlette's debug ServerErrorMiddleware so our handler catches Exception
    app.debug = False

    return app


@pytest.fixture
async def client():
    app = _make_app()
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_http_exception_404(client):
    resp = await client.get("/not-found")
    assert resp.status_code == 404
    data = resp.json()
    assert data["detail"] == "Resource not found"
    assert data["code"] == "HTTP_404"


@pytest.mark.asyncio
async def test_validation_error_422(client):
    resp = await client.post("/validate", json={"wrong": "data"})
    assert resp.status_code == 422
    data = resp.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert isinstance(data["errors"], list)
    assert len(data["errors"]) > 0


@pytest.mark.asyncio
async def test_generic_exception_500(client):
    resp = await client.get("/crash")
    assert resp.status_code == 500
    data = resp.json()
    assert data["detail"] == "Internal server error"
    assert data["code"] == "INTERNAL_ERROR"
    # Must not leak traceback
    assert "RuntimeError" not in data["detail"]


@pytest.mark.asyncio
async def test_register_all_handlers():
    """register_exception_handlers should add 3 handlers."""
    app = FastAPI()
    register_exception_handlers(app)
    # FastAPI stores exception handlers in a dict
    assert len(app.exception_handlers) >= 3


@pytest.mark.asyncio
async def test_error_response_format(client):
    """All error responses have detail, code, and errors keys."""
    resp = await client.get("/not-found")
    data = resp.json()
    assert "detail" in data
    assert "code" in data
    assert "errors" in data
