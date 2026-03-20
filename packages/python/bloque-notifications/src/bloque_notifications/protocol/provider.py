"""Protocol for notification providers."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class NotificationProvider(Protocol):
    """Protocol that all notification providers must satisfy.

    Duck-typed: any object with send and health_check
    can be used as a provider without inheriting this class.

    Example:
        class MyProvider:
            async def send(self, recipient, subject, body, *, metadata=None):
                # deliver the notification
                return {"status": "sent"}

            async def health_check(self) -> bool:
                return True
    """

    async def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...

    async def health_check(self) -> bool: ...
