"""Redis cache with TTL and decorator support."""

from .decorator import cached
from .store import RedisCache

__all__ = ["RedisCache", "cached"]
