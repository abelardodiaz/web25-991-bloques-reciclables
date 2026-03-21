"""E2E test for docs/recetas/mvp-sin-login.md

Tests the backend portion of the MVP recipe. Frontend (React/TSX) is
not testable with pytest - only the Python API is verified here.
"""

from ulfblk_core import create_app
from ulfblk_testing.client import create_test_client

# ---------- Recipe code (copied from docs/recetas/mvp-sin-login.md) ----------

app = create_app(service_name="mvp", version="0.1.0", title="MVP API")


@app.get("/api/data")
async def get_data():
    return {"items": ["uno", "dos", "tres"]}


# ---------- Tests ----------


class TestMVPSinLoginRecipe:
    async def test_health_endpoint(self):
        """create_app() includes /health automatically."""
        async with create_test_client(app) as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            assert resp.json()["service"] == "mvp"

    async def test_data_endpoint_no_auth_required(self):
        """MVP has no auth - endpoint is publicly accessible."""
        async with create_test_client(app) as client:
            resp = await client.get("/api/data")
            assert resp.status_code == 200
            data = resp.json()
            assert data["items"] == ["uno", "dos", "tres"]

    async def test_request_id_header(self):
        """Middleware adds X-Request-ID even without auth."""
        async with create_test_client(app) as client:
            resp = await client.get("/api/data")
            assert "x-request-id" in resp.headers

    async def test_process_time_header(self):
        """Middleware adds X-Process-Time even without auth."""
        async with create_test_client(app) as client:
            resp = await client.get("/api/data")
            assert "x-process-time" in resp.headers

    async def test_no_auth_on_any_endpoint(self):
        """No 401/403 on any endpoint - this is a public MVP."""
        async with create_test_client(app) as client:
            for path in ["/health", "/api/data"]:
                resp = await client.get(path)
                assert resp.status_code == 200, f"{path} returned {resp.status_code}"

    async def test_cors_not_blocking(self):
        """OPTIONS preflight should not fail (no CORS middleware blocking)."""
        async with create_test_client(app) as client:
            resp = await client.options("/api/data")
            assert resp.status_code in (200, 405)
