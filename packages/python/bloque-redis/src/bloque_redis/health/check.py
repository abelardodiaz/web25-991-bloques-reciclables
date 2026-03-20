"""Health check compatible with bloque-core HealthResponse.checks."""

from __future__ import annotations

from ..client.manager import RedisManager


async def redis_health_check(manager: RedisManager) -> dict[str, bool]:
    """Check Redis connectivity.

    Returns a dict compatible with HealthResponse.checks:
        {"redis": True} if ping succeeds, {"redis": False} otherwise.
    """
    reachable = await manager.ping()
    return {"redis": reachable}
