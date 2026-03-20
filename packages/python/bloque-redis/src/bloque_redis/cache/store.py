"""Redis-backed cache with JSON serialization."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from bloque_core.logging import get_logger

from ..client.manager import RedisManager

logger = get_logger(__name__)


class RedisCache:
    """Key-value cache backed by Redis with TTL support.

    Args:
        manager: RedisManager instance (must be connected).
        default_ttl: Default TTL in seconds. None means no expiration.
        serializer: Function to serialize values (default: json.dumps).
        deserializer: Function to deserialize values (default: json.loads).
    """

    def __init__(
        self,
        manager: RedisManager,
        default_ttl: int | None = 300,
        serializer: Callable[[Any], str] = json.dumps,
        deserializer: Callable[[str], Any] = json.loads,
    ) -> None:
        self._manager = manager
        self._default_ttl = default_ttl
        self._serialize = serializer
        self._deserialize = deserializer

    async def get(self, key: str, tenant_id: str | None = None) -> Any | None:
        """Get a cached value. Returns None if key doesn't exist."""
        full_key = self._manager.make_key(key, tenant_id=tenant_id)
        raw = await self._manager.client.get(full_key)
        if raw is None:
            return None
        return self._deserialize(raw)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        tenant_id: str | None = None,
    ) -> None:
        """Set a cached value with optional TTL override."""
        full_key = self._manager.make_key(key, tenant_id=tenant_id)
        serialized = self._serialize(value)
        effective_ttl = ttl if ttl is not None else self._default_ttl
        if effective_ttl is not None:
            await self._manager.client.setex(full_key, effective_ttl, serialized)
        else:
            await self._manager.client.set(full_key, serialized)

    async def delete(self, key: str, tenant_id: str | None = None) -> bool:
        """Delete a cached key. Returns True if the key existed."""
        full_key = self._manager.make_key(key, tenant_id=tenant_id)
        result = await self._manager.client.delete(full_key)
        return result > 0

    async def exists(self, key: str, tenant_id: str | None = None) -> bool:
        """Check if a key exists in cache."""
        full_key = self._manager.make_key(key, tenant_id=tenant_id)
        return await self._manager.client.exists(full_key) > 0

    async def clear_prefix(self, prefix: str, tenant_id: str | None = None) -> int:
        """Delete all keys matching a prefix. Uses SCAN (not KEYS).

        Returns the number of deleted keys.
        """
        full_prefix = self._manager.make_key(prefix, tenant_id=tenant_id)
        pattern = f"{full_prefix}*"
        deleted = 0
        async for key in self._manager.client.scan_iter(match=pattern, count=100):
            await self._manager.client.delete(key)
            deleted += 1
        return deleted
