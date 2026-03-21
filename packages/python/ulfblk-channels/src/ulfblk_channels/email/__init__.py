"""Email channel: inbound webhook and SMTP outbound client."""

from ulfblk_channels.email.client import EmailClient
from ulfblk_channels.email.router import EmailRouter
from ulfblk_channels.models.settings import EmailSettings

__all__ = [
    "EmailClient",
    "EmailRouter",
    "EmailSettings",
]
