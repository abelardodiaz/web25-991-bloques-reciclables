"""Console notification provider."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ConsoleProvider:
    """Log notifications to the console via Python logging.

    Useful for development, testing, and debugging notification flows.

    Args:
        logger_name: Name for the logger instance.

    Example:
        provider = ConsoleProvider()
        await provider.send("user@test.com", "Hello", "World")
        # Logs: [NOTIFICATION] To: user@test.com | Subject: Hello | Body: World
    """

    def __init__(self, logger_name: str = "ulfblk_notifications.console") -> None:
        self._logger = logging.getLogger(logger_name)

    async def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Log the notification.

        Args:
            recipient: Target address.
            subject: Notification subject.
            body: Notification body.
            metadata: Extra data (logged if present).

        Returns:
            Dict with status "logged".
        """
        parts = [
            f"[NOTIFICATION] To: {recipient}",
            f"Subject: {subject}",
            f"Body: {body}",
        ]
        if metadata:
            parts.append(f"Metadata: {metadata}")

        self._logger.info(" | ".join(parts))
        return {"status": "logged"}

    async def health_check(self) -> bool:
        """Console provider is always healthy."""
        return True
