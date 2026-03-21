"""Tests verifying plugin auto-registration."""

from fastapi import FastAPI
from httpx import AsyncClient


class TestPluginFixtures:
    def test_test_app_fixture_available(self, test_app):
        assert isinstance(test_app, FastAPI)

    async def test_test_client_fixture_available(self, test_client):
        assert isinstance(test_client, AsyncClient)
        resp = await test_client.get("/ping")
        assert resp.status_code == 200

    def test_rsa_keys_fixture_available(self, rsa_keys):
        private_pem, public_pem = rsa_keys
        assert "BEGIN PRIVATE KEY" in private_pem
        assert "BEGIN PUBLIC KEY" in public_pem

    def test_jwt_manager_fixture_available(self, jwt_manager):
        assert jwt_manager.private_key is not None

    def test_test_engine_fixture_available(self, test_engine):
        from sqlalchemy.ext.asyncio import AsyncEngine

        assert isinstance(test_engine, AsyncEngine)

    def test_test_session_factory_fixture_available(self, test_session_factory):
        from sqlalchemy.ext.asyncio import async_sessionmaker

        assert isinstance(test_session_factory, async_sessionmaker)
