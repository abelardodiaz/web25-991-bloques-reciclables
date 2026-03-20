"""BloqueSettings: base configuration via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BloqueSettings(BaseSettings):
    """Base settings for Bloque applications.

    Reads from environment variables with prefix BLOQUE_.
    Designed to be subclassed for project-specific settings.

    Example::

        class MySettings(BloqueSettings):
            database_url: str = "sqlite:///db.sqlite3"
    """

    model_config = SettingsConfigDict(
        env_prefix="BLOQUE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    service_name: str = "api"
    version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    log_json_format: bool = False
