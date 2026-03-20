"""Tests for redis_health_check."""

from bloque_redis.client.manager import RedisManager, RedisSettings
from bloque_redis.health.check import redis_health_check


class TestHealthCheck:
    async def test_healthy(self, redis_manager):
        result = await redis_health_check(redis_manager)
        assert result == {"redis": True}

    async def test_unhealthy(self):
        """Disconnected manager returns redis: False."""
        mgr = RedisManager(RedisSettings(url="redis://unreachable:9999"))
        # Don't connect -- ping will fail
        # We need a client that fails ping, so we mock it
        import unittest.mock as mock

        fake_client = mock.AsyncMock()
        fake_client.ping.side_effect = ConnectionError("unreachable")
        mgr._client = fake_client

        result = await redis_health_check(mgr)
        assert result == {"redis": False}
