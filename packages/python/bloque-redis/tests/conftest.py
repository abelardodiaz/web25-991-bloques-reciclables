"""Shared fixtures for bloque-redis tests."""

import fakeredis.aioredis
import pytest
from bloque_redis.client.manager import RedisManager, RedisSettings


@pytest.fixture
def fake_redis():
    """Create a FakeRedis instance (async, decode_responses=True)."""
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def redis_manager(fake_redis):
    """Create a RedisManager pre-wired with FakeRedis (no real connection)."""
    settings = RedisSettings(key_prefix="test")
    manager = RedisManager(settings=settings)
    # Bypass connect() by injecting the fake client directly
    manager._client = fake_redis
    return manager


@pytest.fixture
def tenant_manager(fake_redis):
    """RedisManager with tenant_aware=True."""
    settings = RedisSettings(key_prefix="app", tenant_aware=True)
    manager = RedisManager(settings=settings)
    manager._client = fake_redis
    return manager
