"""Shared fixtures for ulfblk-db tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from ulfblk_db import DatabaseSettings, create_async_engine, create_session_factory


@pytest.fixture
def db_settings() -> DatabaseSettings:
    """DatabaseSettings configured for SQLite in-memory."""
    return DatabaseSettings(database_url="sqlite+aiosqlite:///:memory:")


@pytest.fixture
def async_engine(db_settings: DatabaseSettings) -> AsyncEngine:
    """Async engine using SQLite in-memory."""
    return create_async_engine(db_settings)


@pytest.fixture
def session_factory(async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Session factory bound to the in-memory engine."""
    return create_session_factory(async_engine)
