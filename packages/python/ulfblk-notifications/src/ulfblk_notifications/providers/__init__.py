"""Built-in notification providers."""

from ulfblk_notifications.providers.console import ConsoleProvider
from ulfblk_notifications.providers.webhook import WebhookProvider

__all__ = ["ConsoleProvider", "WebhookProvider"]
