"""Protocol for action handlers."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ulfblk_automation.models.action import Action


@runtime_checkable
class ActionHandler(Protocol):
    """Protocol that all action handlers must satisfy.

    Duck-typed: any object with execute and health_check
    can be used as a handler without inheriting this class.

    Example:
        class WebhookHandler:
            async def execute(self, action, context):
                # POST to action.config["url"]
                return {"status": "sent"}

            async def health_check(self):
                return True
    """

    async def execute(
        self, action: Action, context: dict[str, Any]
    ) -> dict[str, Any]: ...

    async def health_check(self) -> bool: ...
