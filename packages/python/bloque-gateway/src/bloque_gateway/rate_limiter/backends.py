"""Rate limiter backends: in-memory and Redis."""

from __future__ import annotations

import time
from typing import Protocol, runtime_checkable


@runtime_checkable
class RateLimiterBackend(Protocol):
    """Protocol for rate limiter storage backends.

    Returns:
        Tuple of (allowed, remaining, reset_at_epoch).
    """

    async def is_allowed(
        self, key: str, limit: int, window: int
    ) -> tuple[bool, int, int]: ...


class InMemoryBackend:
    """Sliding window rate limiter using in-memory timestamp lists.

    Suitable for single-process deployments. State is lost on restart.
    """

    def __init__(self) -> None:
        self._windows: dict[str, list[float]] = {}

    async def is_allowed(
        self, key: str, limit: int, window: int
    ) -> tuple[bool, int, int]:
        now = time.time()
        cutoff = now - window

        if key not in self._windows:
            self._windows[key] = []

        # Remove expired timestamps
        self._windows[key] = [ts for ts in self._windows[key] if ts > cutoff]

        current_count = len(self._windows[key])
        reset_at = int(now + window)

        if current_count >= limit:
            remaining = 0
            return False, remaining, reset_at

        self._windows[key].append(now)
        remaining = limit - current_count - 1
        return True, remaining, reset_at


class RedisBackend:
    """Sliding window rate limiter using Redis sorted sets.

    Uses ZREMRANGEBYSCORE + ZADD + ZCARD for atomic sliding window.
    Accepts a duck-typed redis_manager with a .client property
    (compatible with bloque_redis.RedisManager without hard import).
    """

    def __init__(self, redis_manager: object) -> None:
        self._redis_manager = redis_manager

    async def is_allowed(
        self, key: str, limit: int, window: int
    ) -> tuple[bool, int, int]:
        client = self._redis_manager.client  # type: ignore[attr-defined]
        now = time.time()
        cutoff = now - window
        reset_at = int(now + window)

        pipe = client.pipeline(transaction=True)
        pipe.zremrangebyscore(key, 0, cutoff)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window)
        results = await pipe.execute()

        current_count = results[1]  # ZCARD result (before ZADD)

        if current_count >= limit:
            # Over limit: remove the ZADD we just did
            await client.zrem(key, str(now))
            return False, 0, reset_at

        remaining = limit - current_count - 1
        return True, remaining, reset_at
