"""ulfblk-notifications - Notification orchestrator with pluggable providers."""

__version__ = "0.1.0"

from ulfblk_notifications.models.notification import (
    Channel,
    ChannelResult,
    DeliveryStatus,
    Notification,
    NotificationResult,
    Priority,
)
from ulfblk_notifications.models.settings import (
    NotificationSettings,
    TemplateSettings,
    WebhookProviderSettings,
)
from ulfblk_notifications.protocol.provider import NotificationProvider
from ulfblk_notifications.providers.console import ConsoleProvider
from ulfblk_notifications.providers.webhook import WebhookProvider
from ulfblk_notifications.service.orchestrator import NotificationService
from ulfblk_notifications.templates.engine import TemplateEngine

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
