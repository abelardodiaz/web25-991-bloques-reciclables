"""bloque-notifications - Notification orchestrator with pluggable providers."""

__version__ = "0.1.0"

from bloque_notifications.models.notification import (
    Channel,
    ChannelResult,
    DeliveryStatus,
    Notification,
    NotificationResult,
    Priority,
)
from bloque_notifications.models.settings import (
    NotificationSettings,
    TemplateSettings,
    WebhookProviderSettings,
)
from bloque_notifications.protocol.provider import NotificationProvider
from bloque_notifications.providers.console import ConsoleProvider
from bloque_notifications.providers.webhook import WebhookProvider
from bloque_notifications.service.orchestrator import NotificationService
from bloque_notifications.templates.engine import TemplateEngine

__all__ = [
    "Channel",
    "ChannelResult",
    "ConsoleProvider",
    "DeliveryStatus",
    "Notification",
    "NotificationProvider",
    "NotificationResult",
    "NotificationService",
    "NotificationSettings",
    "Priority",
    "TemplateEngine",
    "TemplateSettings",
    "WebhookProvider",
    "WebhookProviderSettings",
]
