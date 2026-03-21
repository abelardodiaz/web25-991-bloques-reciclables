"""Tests for engine factory and health check."""

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool import StaticPool

from ulfblk_db import DatabaseSettings, create_async_engine, db_health_check


class TestCreateAsyncEngine:
    def test_returns_async_engine(self, db_settings):
        engine = create_async_engine(db_settings)
        assert isinstance(engine, AsyncEngine)

    def test_none_settings_uses_defaults(self):
        engine = create_async_engine(None)
        assert isinstance(engine, AsyncEngine)
        assert "postgresql" in str(engine.url)

    def test_sqlite_uses_static_pool(self, db_settings):
        engine = create_async_engine(db_settings)
        assert isinstance(engine.pool, StaticPool)


class TestDbHealthCheck:
    async def test_health_ok(self, async_engine):
        result = await db_health_check(async_engine)
        assert result is True

    async def test_health_fails_bad_url(self):
        bad_settings = DatabaseSettings(
            database_url="sqlite+aiosqlite:///nonexistent/path/to/db.sqlite"
        )
        engine = create_async_engine(bad_settings)
        result = await db_health_check(engine)
        assert result is False
