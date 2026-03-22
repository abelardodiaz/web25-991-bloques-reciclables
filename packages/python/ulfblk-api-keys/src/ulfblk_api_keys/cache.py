"""In-memory cache with TTL for validated API keys."""

from __future__ import annotations

import time
from typing import Any


class InMemoryCache:
    """Simple dict-based cache with per-entry TTL.

    No external dependencies (no Redis required).

    Example::

        cache = InMemoryCache(default_ttl=60)
        cache.set("key_hash", {"project_code": "991"})
        data = cache.get("key_hash")  # Returns dict or None
    """

    def __init__(self, default_ttl: int = 60) -> None:
        self._store: dict[str, tuple[float, Any]] = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        """Get value if exists and not expired."""
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value with TTL (seconds)."""
        actual_ttl = ttl if ttl is not None else self._default_ttl
        self._store[key] = (time.monotonic() + actual_ttl, value)

    def invalidate(self, key: str) -> bool:
        """Remove a specific key. Returns True if it existed."""
        return self._store.pop(key, None) is not None

    def clear(self) -> None:
        """Remove all entries."""
        self._store.clear()

    @property
    def size(self) -> int:
        """Number of entries (including potentially expired ones)."""
        return len(self._store)
