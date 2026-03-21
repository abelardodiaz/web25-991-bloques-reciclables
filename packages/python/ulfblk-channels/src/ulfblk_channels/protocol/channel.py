"""Protocol for channel implementations."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ulfblk_channels.models.message import OutboundMessage


@runtime_checkable
class ChannelProtocol(Protocol):
    """Protocol that all channel clients must satisfy.

    Duck-typed: any object with send_message and health_check
    can be used as a channel without inheriting this class.
    """

    async def send_message(self, message: OutboundMessage) -> dict[str, Any]: ...

    async def health_check(self) -> bool: ...
