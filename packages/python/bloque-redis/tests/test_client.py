"""Tests for RedisManager and RedisSettings."""

import pytest
from bloque_redis.client.manager import RedisManager, RedisSettings


class TestRedisSettings:
    def test_defaults(self):
        s = RedisSettings()
        assert s.url == "redis://localhost:6379/0"
        assert s.max_connections == 10
        assert s.socket_timeout == 5.0
        assert s.decode_responses is True
        assert s.key_prefix == ""
        assert s.tenant_aware is False

    def test_custom(self):
        s = RedisSettings(url="redis://custom:6380/1", key_prefix="myapp")
        assert s.url == "redis://custom:6380/1"
        assert s.key_prefix == "myapp"


class TestRedisManagerMakeKey:
    def test_no_prefix(self):
        mgr = RedisManager(RedisSettings())
        assert mgr.make_key("session:abc") == "session:abc"

    def test_with_prefix(self):
        mgr = RedisManager(RedisSettings(key_prefix="app"))
        assert mgr.make_key("session:abc") == "app:session:abc"

    def test_with_tenant_explicit(self):
        mgr = RedisManager(RedisSettings(key_prefix="app"))
        assert mgr.make_key("session:abc", tenant_id="t1") == "app:t1:session:abc"

    def test_tenant_aware_no_context(self):
        """tenant_aware=True but no multitenant installed -> no tenant prefix."""
        mgr = RedisManager(RedisSettings(key_prefix="app", tenant_aware=True))
        # Without bloque_multitenant context set, should fall back to no tenant
        assert mgr.make_key("key") == "app:key"

    def test_explicit_tenant_overrides_context(self):
        """Explicit tenant_id takes priority even with tenant_aware=True."""
        mgr = RedisManager(RedisSettings(key_prefix="app", tenant_aware=True))
        assert mgr.make_key("key", tenant_id="explicit") == "app:explicit:key"


class TestRedisManagerLifecycle:
    async def test_client_not_connected_raises(self):
        mgr = RedisManager()
        with pytest.raises(RuntimeError, match="not connected"):
            _ = mgr.client

    async def test_ping(self, redis_manager):
        result = await redis_manager.ping()
        assert result is True

    async def test_context_manager(self, fake_redis):
        settings = RedisSettings()
        mgr = RedisManager(settings=settings)
        mgr._client = fake_redis
        async with mgr as m:
            assert await m.ping() is True
        assert mgr._client is None
