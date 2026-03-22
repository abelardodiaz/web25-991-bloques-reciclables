"""SchedulingSettings: scheduling configuration extending BloqueSettings."""

from pydantic_settings import SettingsConfigDict
from ulfblk_core import BloqueSettings


class SchedulingSettings(BloqueSettings):
    """Scheduling configuration with appointment and slot defaults.

    Reads from environment variables with BLOQUE_SCHEDULING_ prefix.

    Example::

        settings = SchedulingSettings()
        # Or override via env: BLOQUE_SCHEDULING_DEFAULT_DURATION_MINUTES=60
    """

    model_config = SettingsConfigDict(
        env_prefix="BLOQUE_SCHEDULING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    default_duration_minutes: int = 30
    min_advance_hours: int = 1
    max_advance_days: int = 60
    buffer_minutes: int = 0
    timezone: str = "UTC"
