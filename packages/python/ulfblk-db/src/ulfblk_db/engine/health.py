"""Database health check."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


async def db_health_check(engine: AsyncEngine) -> bool:
    """Check database connectivity by executing SELECT 1.

    Designed for use with HealthResponse.checks:
        checks = {"database": await db_health_check(engine)}

    Args:
        engine: AsyncEngine to check.

    Returns:
        True if the database is reachable, False otherwise.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
