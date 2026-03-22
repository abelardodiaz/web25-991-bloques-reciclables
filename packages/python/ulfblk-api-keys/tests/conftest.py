"""Shared fixtures for ulfblk-api-keys tests."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from ulfblk_api_keys import ApiKeyConfig, ApiKeyService, InMemoryCache
from ulfblk_api_keys.models import ApiKeyModel, KeyAuditLog  # noqa: F401 - register models
from ulfblk_db import Base


@pytest.fixture
def config():
    return ApiKeyConfig(
        prefix="test",
        max_keys_per_project=3,
        grace_period_days=7,
        cache_ttl_seconds=60,
        master_secret="test-master-secret-123",
    )


@pytest.fixture
def cache():
    return InMemoryCache(default_ttl=60)


@pytest.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
def service(config, cache):
    return ApiKeyService(config=config, cache=cache)
