"""Health check for notification providers."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def notifications_health_check(
    providers: dict[str, Any],
) -> dict[str, bool]:
    """Check health of all registered providers.

    Args:
        providers: Mapping of channel name -> provider instance.

    Returns:
        Dict mapping channel name -> health status (True/False).
    """
    results: dict[str, bool] = {}
    for name, provider in providers.items():
        try:
            if hasattr(provider, "health_check"):
                results[name] = await provider.health_check()
            else:
                results[name] = True
        except Exception as exc:
            logger.warning("Health check failed for %s: %s", name, exc)
            results[name] = False
    return results
