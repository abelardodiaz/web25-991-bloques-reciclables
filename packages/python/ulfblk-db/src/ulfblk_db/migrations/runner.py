"""Migration runner: init, create, upgrade, downgrade."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase

from .config import MigrationSettings
from .env_template import ALEMBIC_INI_TEMPLATE, ENV_PY_TEMPLATE, SCRIPT_PY_MAKO_TEMPLATE


def init_migrations(
    settings: MigrationSettings | None = None,
) -> Path:
    """Initialize Alembic migrations directory with async-ready templates.

    Creates:
      migrations/
        env.py          - Alembic environment (sync, works with async engines)
        script.py.mako  - Migration script template
        versions/        - Migration files directory
      alembic.ini        - Alembic configuration

    Args:
        settings: Migration settings. Uses defaults if None.

    Returns:
        Path to the created migrations directory.
    """
    if settings is None:
        settings = MigrationSettings()

    migrations_dir = Path(settings.migrations_dir)
    versions_dir = migrations_dir / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)

    # Write env.py
    env_path = migrations_dir / "env.py"
    if not env_path.exists():
        env_path.write_text(ENV_PY_TEMPLATE, encoding="utf-8")

    # Write script.py.mako
    mako_path = migrations_dir / "script.py.mako"
    if not mako_path.exists():
        mako_path.write_text(SCRIPT_PY_MAKO_TEMPLATE, encoding="utf-8")

    # Write alembic.ini in parent directory
    ini_path = migrations_dir.parent / "alembic.ini"
    if not ini_path.exists():
        ini_content = ALEMBIC_INI_TEMPLATE.replace(
            "script_location = %(here)s/versions",
            f"script_location = {migrations_dir}",
        )
        # Inject database URL
        ini_content = f"# sqlalchemy.url is set dynamically from DatabaseSettings\nsqlalchemy.url = {settings.database_url}\n\n{ini_content}"
        ini_path.write_text(ini_content, encoding="utf-8")

    return migrations_dir


def create_migration(
    message: str,
    settings: MigrationSettings | None = None,
    autogenerate: bool = True,
) -> str:
    """Create a new migration revision.

    Args:
        message: Migration description.
        settings: Migration settings.
        autogenerate: Auto-detect model changes.

    Returns:
        Path to the generated migration file.
    """
    from alembic import command
    from alembic.config import Config

    if settings is None:
        settings = MigrationSettings()

    alembic_cfg = _get_alembic_config(settings)

    if autogenerate:
        command.revision(alembic_cfg, message=message, autogenerate=True)
    else:
        command.revision(alembic_cfg, message=message)

    return str(Path(settings.migrations_dir) / "versions")


def run_upgrade(
    settings: MigrationSettings | None = None,
    revision: str = "head",
) -> None:
    """Apply pending migrations.

    Args:
        settings: Migration settings.
        revision: Target revision (default "head" = latest).
    """
    from alembic import command

    if settings is None:
        settings = MigrationSettings()

    alembic_cfg = _get_alembic_config(settings)
    command.upgrade(alembic_cfg, revision)


def run_downgrade(
    settings: MigrationSettings | None = None,
    revision: str = "-1",
) -> None:
    """Rollback migrations.

    Args:
        settings: Migration settings.
        revision: Target revision (default "-1" = one step back).
    """
    from alembic import command

    if settings is None:
        settings = MigrationSettings()

    alembic_cfg = _get_alembic_config(settings)
    command.downgrade(alembic_cfg, revision)


def _get_alembic_config(settings: MigrationSettings):
    """Build Alembic Config from MigrationSettings."""
    from alembic.config import Config

    migrations_dir = Path(settings.migrations_dir)
    ini_path = migrations_dir.parent / "alembic.ini"

    if ini_path.exists():
        alembic_cfg = Config(str(ini_path))
    else:
        alembic_cfg = Config()

    alembic_cfg.set_main_option("script_location", str(migrations_dir))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

    return alembic_cfg
