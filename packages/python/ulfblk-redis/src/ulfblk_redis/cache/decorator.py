"""Caching decorator for async functions."""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from typing import Any

from .store import RedisCache


def _default_key_builder(func: Callable, args: tuple, kwargs: dict) -> str:
    """Build a cache key from function name and arguments."""
    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    parts = [func.__module__, func.__qualname__]
    for name, value in bound.arguments.items():
        parts.append(f"{name}={value!r}")
    return ":".join(parts)


def cached(
    cache: RedisCache,
    ttl: int | None = None,
    key_builder: Callable[[Callable, tuple, dict], str] | None = None,
) -> Callable:
    """Decorator to cache the result of an async function.

    Args:
        cache: RedisCache instance.
        ttl: Optional TTL override (seconds).
        key_builder: Optional custom key builder function.

    Example::

        @cached(cache, ttl=60)
        async def get_user(user_id: str) -> dict:
            ...
    """
    builder = key_builder or _default_key_builder

    def decorator(func: Callable) -> Callable:
        if not inspect.iscoroutinefunction(func):
            raise TypeError(f"@cached can only decorate async functions, got {func!r}")

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = builder(func, args, kwargs)
            hit = await cache.get(key)
            if hit is not None:
                return hit
            result = await func(*args, **kwargs)
            await cache.set(key, result, ttl=ttl)
            return result

        return wrapper

    return decorator
