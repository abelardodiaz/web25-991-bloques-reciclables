"""Migration settings."""

from __future__ import annotations

from ulfblk_db.config.settings import DatabaseSettings


class MigrationSettings(DatabaseSettings):
    """Settings for database migrations.

    Extends DatabaseSettings with migration-specific config.

    Example::

        settings = MigrationSettings(migrations_dir="./db/migrations")
    """

    migrations_dir: str = "./migrations"
