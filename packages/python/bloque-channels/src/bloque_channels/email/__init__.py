"""Email channel: inbound webhook and SMTP outbound client."""

from bloque_channels.email.client import EmailClient
from bloque_channels.email.router import EmailRouter
from bloque_channels.models.settings import EmailSettings

__all__ = [
    "EmailClient",
    "EmailRouter",
    "EmailSettings",
]
