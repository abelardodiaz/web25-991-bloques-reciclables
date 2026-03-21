"""Notification data models."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class Channel(StrEnum):
    """Supported notification channels."""

    EMAIL = "email"
    WEBHOOK = "webhook"
    PUSH = "push"
    CONSOLE = "console"


class Priority(StrEnum):
    """Notification priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class DeliveryStatus(StrEnum):
    """Delivery outcome for a single channel."""

    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Notification:
    """A notification request to be processed by the service.

    Args:
        recipient: Target address (email, URL, user ID, etc.).
        template_name: Name of the registered template to render.
        context: Variables for template rendering.
        channels: Which channels to deliver on. Falls back to service defaults.
        priority: Delivery priority.
        subject: Explicit subject (bypasses template subject rendering).
        metadata: Extra data passed through to providers.
        tenant_id: Tenant identifier for multi-tenant template resolution.
    """

    recipient: str
    template_name: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    channels: list[Channel] = field(default_factory=list)
    priority: Priority = Priority.NORMAL
    subject: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    tenant_id: str | None = None


@dataclass(frozen=True)
class ChannelResult:
    """Delivery result for a single channel.

    Args:
        channel: The channel that was used.
        status: Outcome of the delivery attempt.
        detail: Provider-specific response data.
        error: Error message if delivery failed.
    """

    channel: Channel
    status: DeliveryStatus
    detail: dict[str, Any] = field(default_factory=dict)
    error: str = ""


@dataclass(frozen=True)
class NotificationResult:
    """Aggregate result of a notification across all channels.

    Args:
        notification_id: Unique identifier for this notification.
        results: Per-channel delivery results.
        rendered_subject: The subject after template rendering.
        rendered_body: The body after template rendering.
        timestamp: When the notification was processed.
    """

    notification_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    results: list[ChannelResult] = field(default_factory=list)
    rendered_subject: str = ""
    rendered_body: str = ""
    timestamp: datetime | None = field(
        default_factory=lambda: datetime.now(UTC)
    )
