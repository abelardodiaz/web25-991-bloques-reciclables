"""Tests for RedisCache and @cached decorator."""

import pytest
from bloque_redis.cache.decorator import cached
from bloque_redis.cache.store import RedisCache


@pytest.fixture
def cache(redis_manager):
    return RedisCache(redis_manager, default_ttl=300)


class TestRedisCache:
    async def test_set_and_get(self, cache):
        await cache.set("user:1", {"name": "Alice"})
        result = await cache.get("user:1")
        assert result == {"name": "Alice"}

    async def test_get_missing_key(self, cache):
        result = await cache.get("nonexistent")
        assert result is None

    async def test_delete_existing(self, cache):
        await cache.set("to_delete", "value")
        deleted = await cache.delete("to_delete")
        assert deleted is True
        assert await cache.get("to_delete") is None

    async def test_delete_missing(self, cache):
        deleted = await cache.delete("never_existed")
        assert deleted is False

    async def test_exists(self, cache):
        await cache.set("check_me", 42)
        assert await cache.exists("check_me") is True
        assert await cache.exists("nope") is False

    async def test_clear_prefix(self, cache):
        await cache.set("products:1", "a")
        await cache.set("products:2", "b")
        await cache.set("users:1", "c")
        deleted = await cache.clear_prefix("products:")
        assert deleted == 2
        assert await cache.exists("products:1") is False
        assert await cache.exists("users:1") is True

    async def test_custom_ttl(self, cache):
        await cache.set("short", "data", ttl=1)
        result = await cache.get("short")
        assert result == "data"

    async def test_no_default_ttl(self, redis_manager):
        """Cache with no default TTL sets keys without expiration."""
        cache = RedisCache(redis_manager, default_ttl=None)
        await cache.set("permanent", "value")
        result = await cache.get("permanent")
        assert result == "value"


class TestCachedDecorator:
    async def test_caches_result(self, cache):
        call_count = 0

        @cached(cache, ttl=60)
        async def expensive(x: int) -> dict:
            nonlocal call_count
            call_count += 1
            return {"result": x * 2}

        r1 = await expensive(5)
        r2 = await expensive(5)
        assert r1 == {"result": 10}
        assert r2 == {"result": 10}
        assert call_count == 1  # second call served from cache

    async def test_different_args_different_keys(self, cache):
        @cached(cache)
        async def compute(a: int, b: int) -> int:
            return a + b

        assert await compute(1, 2) == 3
        assert await compute(3, 4) == 7

    async def test_rejects_sync_function(self, cache):
        with pytest.raises(TypeError, match="async"):

            @cached(cache)
            def not_async():
                pass

    async def test_custom_key_builder(self, cache):
        def my_builder(func, args, kwargs):
            return f"custom:{args[0]}"

        @cached(cache, key_builder=my_builder)
        async def fetch(item_id: str) -> str:
            return f"item-{item_id}"

        result = await fetch("abc")
        assert result == "item-abc"
        # Verify the custom key was used
        stored = await cache.get("custom:abc")
        assert stored == "item-abc"
