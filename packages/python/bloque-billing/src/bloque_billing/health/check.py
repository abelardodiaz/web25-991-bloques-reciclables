"""Billing health check utility."""

from __future__ import annotations

from typing import Any


async def billing_health_check(
    provider: Any | None = None,
) -> dict[str, bool]:
    """Check billing provider health.

    Args:
        provider: A billing provider with a health_check() method.

    Returns:
        Dict with health status, e.g. {"billing": True}.
    """
    if provider is None:
        return {"billing": False}

    try:
        healthy = await provider.health_check()
        return {"billing": healthy}
    except Exception:
        return {"billing": False}
