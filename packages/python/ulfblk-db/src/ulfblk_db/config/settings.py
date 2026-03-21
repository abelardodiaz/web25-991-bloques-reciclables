"""DatabaseSettings: database configuration extending BloqueSettings."""

from ulfblk_core import BloqueSettings


class DatabaseSettings(BloqueSettings):
    """Database configuration with connection pool settings.

    Reads from environment variables with BLOQUE_ prefix.

    Example::

        settings = DatabaseSettings()
        # Or override via env: BLOQUE_DATABASE_URL=postgresql+asyncpg://...
    """

    database_url: str = "postgresql+asyncpg://localhost:5432/bloquedb"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_echo: bool = False
