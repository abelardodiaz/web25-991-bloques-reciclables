"""Core message models for all channels."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class ChannelType(StrEnum):
    """Supported channel types."""

    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    EMAIL = "email"


@dataclass(frozen=True)
class InboundMessage:
    """Incoming message from any channel.

    Frozen dataclass for immutability. The ``raw`` field holds
    the original payload from the channel for advanced use cases.
    """

    channel: ChannelType
    sender: str
    text: str
    message_id: str
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    tenant_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class OutboundMessage:
    """Outgoing message to send through a channel."""

    recipient: str
    text: str
    channel: ChannelType | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
