"""Built-in log action handler."""

from __future__ import annotations

import logging
from typing import Any

from bloque_automation.models.action import Action


class LogActionHandler:
    """Action handler that logs the action and context.

    Built-in handler with zero external dependencies.
    Useful for debugging, auditing, and as a reference implementation.

    Args:
        logger_name: Name for the logger instance.
    """

    def __init__(self, logger_name: str = "bloque_automation.log_handler") -> None:
        self._logger = logging.getLogger(logger_name)

    async def execute(self, action: Action, context: dict[str, Any]) -> dict[str, Any]:
        """Log the action execution."""
        self._logger.info(
            "Action executed: %s | config=%s | context_keys=%s",
            action.name or action.action_type,
            action.config,
            list(context.keys()),
        )
        return {"status": "logged"}

    async def health_check(self) -> bool:
        """Always healthy."""
        return True
