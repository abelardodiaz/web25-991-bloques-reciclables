"""Tests a complete FastAPI app using all bloques together."""

from ulfblk_testing.auth import create_test_token
from ulfblk_testing.client import create_authenticated_client, create_test_client


class TestFullStack:
    async def test_health_works(self, integration_app):
        """Health endpoint responds from the composed app."""
        async with create_test_client(integration_app) as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            assert resp.json()["status"] == "healthy"

    async def test_unauthenticated_rejected(self, integration_app):
        """Unauthenticated request to protected endpoint returns 401."""
        async with create_test_client(integration_app) as client:
            resp = await client.get("/api/users")
            assert resp.status_code in (401, 403)

    async def test_authenticated_returns_tenant_data(self, integration_app, jwt_manager):
        """Authenticated acme user only sees acme users."""
        token = create_test_token(
            jwt_manager, user_id="1", tenant_id="acme", roles=["admin"]
        )
        async with create_authenticated_client(integration_app, token) as client:
            resp = await client.get("/api/users")
            assert resp.status_code == 200
            users = resp.json()["users"]
            assert len(users) >= 1
            assert all(u["tenant_id"] == "acme" for u in users)

    async def test_tenant_isolation(self, integration_app, jwt_manager):
        """Different tenants see different data."""
        acme_token = create_test_token(
            jwt_manager, user_id="1", tenant_id="acme", roles=["admin"]
        )
        globex_token = create_test_token(
            jwt_manager, user_id="2", tenant_id="globex", roles=["admin"]
        )

        async with create_authenticated_client(integration_app, acme_token) as client:
            acme_resp = await client.get("/api/users")
        async with create_authenticated_client(integration_app, globex_token) as client:
            globex_resp = await client.get("/api/users")

        acme_users = acme_resp.json()["users"]
        globex_users = globex_resp.json()["users"]

        acme_emails = {u["email"] for u in acme_users}
        globex_emails = {u["email"] for u in globex_users}

        assert "admin@acme.com" in acme_emails
        assert "admin@globex.com" not in acme_emails
        assert "admin@globex.com" in globex_emails
        assert "admin@acme.com" not in globex_emails

    async def test_create_user_persists(self, integration_app, jwt_manager):
        """POST creates a user that appears in subsequent GET."""
        token = create_test_token(
            jwt_manager,
            user_id="1",
            tenant_id="acme",
            roles=["admin"],
        )
        async with create_authenticated_client(integration_app, token) as client:
            # Create
            create_resp = await client.post("/api/users")
            assert create_resp.status_code == 200
            new_email = create_resp.json()["email"]

            # Verify persistence
            list_resp = await client.get("/api/users")
            emails = {u["email"] for u in list_resp.json()["users"]}
            assert new_email in emails
