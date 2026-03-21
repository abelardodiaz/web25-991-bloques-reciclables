"""E2E test for docs/recetas/api-simple.md

Copies the EXACT code from the recipe and verifies it works:
health check, pagination, middleware headers, error handling.
"""

from ulfblk_core import create_app
from ulfblk_core.schemas import PaginatedResponse
from ulfblk_testing.client import create_test_client

# ---------- Recipe code (copied verbatim from docs/recetas/api-simple.md) ----------

app = create_app(
    service_name="mi-api",
    version="0.1.0",
    title="Mi API",
)


@app.get("/items", response_model=PaginatedResponse[dict])
async def list_items(page: int = 1, size: int = 20):
    items = [{"id": i, "name": f"Item {i}"} for i in range(1, 21)]
    start = (page - 1) * size
    return PaginatedResponse.create(
        items=items[start : start + size],
        total=len(items),
        page=page,
        page_size=size,
    )


# ---------- Tests ----------


class TestApiSimpleRecipe:
    async def test_health_endpoint(self):
        async with create_test_client(app) as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "healthy"
            assert data["service"] == "mi-api"
            assert data["version"] == "0.1.0"

    async def test_items_default_pagination(self):
        async with create_test_client(app) as client:
            resp = await client.get("/items")
            assert resp.status_code == 200
            data = resp.json()
            assert data["total"] == 20
            assert len(data["items"]) == 20
            assert data["items"][0]["id"] == 1
            assert data["items"][19]["id"] == 20

    async def test_items_custom_pagination(self):
        async with create_test_client(app) as client:
            resp = await client.get("/items?page=2&size=5")
            assert resp.status_code == 200
            data = resp.json()
            assert data["total"] == 20
            assert len(data["items"]) == 5
            assert data["items"][0]["id"] == 6

    async def test_request_id_header(self):
        async with create_test_client(app) as client:
            resp = await client.get("/health")
            assert "x-request-id" in resp.headers

    async def test_process_time_header(self):
        async with create_test_client(app) as client:
            resp = await client.get("/health")
            assert "x-process-time" in resp.headers

    async def test_not_found_returns_error(self):
        async with create_test_client(app) as client:
            resp = await client.get("/nonexistent")
            assert resp.status_code == 404
