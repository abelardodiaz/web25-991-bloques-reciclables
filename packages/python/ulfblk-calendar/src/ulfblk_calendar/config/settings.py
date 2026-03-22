"""CalendarSettings: calendar configuration extending BloqueSettings."""

from pydantic_settings import SettingsConfigDict
from ulfblk_core import BloqueSettings


class CalendarSettings(BloqueSettings):
    """Calendar configuration with provider-specific settings.

    Reads from environment variables with BLOQUE_CALENDAR_ prefix.

    Example::

        settings = CalendarSettings()
        # Or override via env: BLOQUE_CALENDAR_TIMEZONE=America/New_York
    """

    model_config = SettingsConfigDict(
        env_prefix="BLOQUE_CALENDAR_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_credentials_path: str = ""
    google_calendar_id: str = ""
    timezone: str = "UTC"
