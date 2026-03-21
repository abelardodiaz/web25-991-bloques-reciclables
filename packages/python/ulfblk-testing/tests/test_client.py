"""Tests for HTTP test client factories."""

from fastapi import FastAPI, Request
from httpx import AsyncClient

from ulfblk_testing import create_authenticated_client, create_test_client


def _make_app() -> FastAPI:
    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"message": "pong"}

    @app.get("/auth-check")
    async def auth_check(request: Request):
        auth = request.headers.get("authorization", "")
        return {"auth": auth}

    @app.get("/header-check")
    async def header_check(request: Request):
        return {"x-custom": request.headers.get("x-custom", "")}

    return app


class TestCreateTestClient:
    async def test_creates_async_client(self):
        app = _make_app()
        async with create_test_client(app) as client:
            assert isinstance(client, AsyncClient)

    async def test_get_request(self):
        app = _make_app()
        async with create_test_client(app) as client:
            resp = await client.get("/ping")
            assert resp.status_code == 200
            assert resp.json() == {"message": "pong"}

    async def test_custom_base_url(self):
        app = _make_app()
        async with create_test_client(app, base_url="http://myapp") as client:
            resp = await client.get("/ping")
            assert resp.status_code == 200

    async def test_extra_kwargs_passed(self):
        app = _make_app()
        async with create_test_client(app, timeout=5.0) as client:
            assert client.timeout.read == 5.0


class TestCreateAuthenticatedClient:
    async def test_includes_auth_header(self):
        app = _make_app()
        async with create_authenticated_client(app, "test-token-123") as client:
            resp = await client.get("/auth-check")
            data = resp.json()
            assert data["auth"] == "Bearer test-token-123"

    async def test_preserves_existing_headers(self):
        app = _make_app()
        async with create_authenticated_client(
            app, "tok", headers={"X-Custom": "val"}
        ) as client:
            resp = await client.get("/header-check")
            assert resp.json()["x-custom"] == "val"
