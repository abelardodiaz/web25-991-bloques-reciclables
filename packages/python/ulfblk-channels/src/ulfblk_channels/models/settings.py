"""Settings for each channel."""

from __future__ import annotations

from ulfblk_core import BloqueSettings
from pydantic_settings import SettingsConfigDict


class WhatsAppSettings(BloqueSettings):
    """Configuration for WhatsApp Meta Cloud API.

    Reads from environment variables with prefix BLOQUE_WHATSAPP_.
    Example: BLOQUE_WHATSAPP_API_TOKEN=your_token
    """

    model_config = SettingsConfigDict(
        env_prefix="BLOQUE_WHATSAPP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_token: str = ""
    verify_token: str = ""
    phone_number_id: str = ""
    api_version: str = "v21.0"
    api_base_url: str = "https://graph.facebook.com"


class TelegramSettings(BloqueSettings):
    """Configuration for Telegram Bot API.

    Reads from environment variables with prefix BLOQUE_TELEGRAM_.
    Example: BLOQUE_TELEGRAM_BOT_TOKEN=123:ABC
    """

    model_config = SettingsConfigDict(
        env_prefix="BLOQUE_TELEGRAM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = ""
    secret_token: str | None = None
    api_base_url: str = "https://api.telegram.org"


class EmailSettings(BloqueSettings):
    """Configuration for email (SMTP outbound + webhook inbound).

    Reads from environment variables with prefix BLOQUE_EMAIL_.
    Example: BLOQUE_EMAIL_SMTP_HOST=smtp.gmail.com
    """

    model_config = SettingsConfigDict(
        env_prefix="BLOQUE_EMAIL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    from_address: str = ""
    webhook_secret: str | None = None
