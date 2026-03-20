"""Health check for registered action handlers."""

from __future__ import annotations

from typing import Any


async def automation_health_check(handlers: dict[str, Any]) -> dict[str, bool]:
    """Check health of all registered action handlers.

    Args:
        handlers: Mapping of action_type -> handler instance.

    Returns:
        Dict of action_type -> health status (True/False).
    """
    results: dict[str, bool] = {}
    for action_type, handler in handlers.items():
        try:
            results[action_type] = await handler.health_check()
        except Exception:
            results[action_type] = False
    return results
