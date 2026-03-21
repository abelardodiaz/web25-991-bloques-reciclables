"""Tests that JWT auth from bloque-auth works alongside database queries from bloque-db."""

from sqlalchemy import select

from bloque_testing.auth import create_test_token

from .conftest import User


class TestAuthWithDatabase:
    async def test_token_user_id_maps_to_db_user(self, db_session, sample_data, jwt_manager):
        """JWT token user_id can be used to query a real DB user."""
        acme_user = sample_data["acme_user"]
        token = create_test_token(
            jwt_manager, user_id=str(acme_user.id), tenant_id="acme"
        )
        data = jwt_manager.decode_token(token)

        result = await db_session.execute(
            select(User).where(User.id == int(data.user_id))
        )
        db_user = result.scalar_one()
        assert db_user.email == "admin@acme.com"

    async def test_token_tenant_matches_db_user(self, db_session, sample_data, jwt_manager):
        """Token tenant_id matches the user's tenant_id in the database."""
        acme_user = sample_data["acme_user"]
        token = create_test_token(
            jwt_manager, user_id=str(acme_user.id), tenant_id=acme_user.tenant_id
        )
        data = jwt_manager.decode_token(token)

        result = await db_session.execute(
            select(User).where(User.id == int(data.user_id))
        )
        db_user = result.scalar_one()
        assert data.tenant_id == db_user.tenant_id

    async def test_token_roles_survive_roundtrip(self, jwt_manager):
        """Roles set in token creation survive decode."""
        token = create_test_token(
            jwt_manager,
            user_id="u-1",
            tenant_id="acme",
            roles=["admin", "manager"],
            permissions=["users:read", "orders:write"],
        )
        data = jwt_manager.decode_token(token)
        assert set(data.roles) == {"admin", "manager"}
        assert set(data.permissions) == {"users:read", "orders:write"}

    async def test_refresh_token_maps_to_db_user(self, db_session, sample_data, jwt_manager):
        """Refresh token sub claim maps to a real DB user."""
        acme_user = sample_data["acme_user"]
        refresh = jwt_manager.create_refresh_token(
            user_id=str(acme_user.id), tenant_id="acme"
        )
        data = jwt_manager.decode_token(refresh)
        assert data.token_type == "refresh"

        result = await db_session.execute(
            select(User).where(User.id == int(data.user_id))
        )
        assert result.scalar_one() is not None
