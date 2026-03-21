"""Async engine factory."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine as _sa_create_async_engine
from sqlalchemy.pool import StaticPool

from ulfblk_db.config.settings import DatabaseSettings


def create_async_engine(settings: DatabaseSettings | None = None) -> AsyncEngine:
    """Create an async SQLAlchemy engine from DatabaseSettings.

    Args:
        settings: Database settings. Uses defaults if None.

    Returns:
        Configured AsyncEngine instance.

    Notes:
        For SQLite URLs (used in testing), automatically configures
        StaticPool and check_same_thread=False for async compatibility.
    """
    if settings is None:
        settings = DatabaseSettings()

    url = settings.database_url

    if url.startswith("sqlite"):
        return _sa_create_async_engine(
            url,
            echo=settings.db_echo,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )

    return _sa_create_async_engine(
        url,
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
    )
