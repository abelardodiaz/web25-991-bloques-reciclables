"""Settings dataclasses for each channel."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WhatsAppSettings:
    """Configuration for WhatsApp Meta Cloud API."""

    api_token: str = ""
    verify_token: str = ""
    phone_number_id: str = ""
    api_version: str = "v21.0"
    api_base_url: str = "https://graph.facebook.com"


@dataclass
class TelegramSettings:
    """Configuration for Telegram Bot API."""

    bot_token: str = ""
    secret_token: str | None = None
    api_base_url: str = "https://api.telegram.org"


@dataclass
class EmailSettings:
    """Configuration for email (SMTP outbound + webhook inbound)."""

    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    from_address: str = ""
    webhook_secret: str | None = None
