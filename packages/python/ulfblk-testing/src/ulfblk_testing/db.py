"""Database testing utilities: in-memory engine, session factory, table creation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
    from sqlalchemy.orm import DeclarativeBase


def create_test_engine(
    database_url: str = "sqlite+aiosqlite:///:memory:",
    echo: bool = False,
) -> AsyncEngine:
    """Create an async engine configured for testing (SQLite in-memory).

    Args:
        database_url: Database URL. Defaults to SQLite in-memory.
        echo: Whether to echo SQL statements.

    Returns:
        AsyncEngine with StaticPool for SQLite compatibility.
    """
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.pool import StaticPool

    if database_url.startswith("sqlite"):
        return create_async_engine(
            database_url,
            echo=echo,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
    return create_async_engine(database_url, echo=echo)


def create_test_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create a session factory bound to the given engine.

    Args:
        engine: AsyncEngine instance.

    Returns:
        async_sessionmaker with expire_on_commit=False.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def create_tables(
    engine: AsyncEngine,
    base: type[DeclarativeBase],
) -> None:
    """Create all tables for the given Base in the engine.

    Args:
        engine: AsyncEngine instance.
        base: SQLAlchemy DeclarativeBase subclass with model metadata.

    Example::

        engine = create_test_engine()
        await create_tables(engine, Base)
    """
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)


async def drop_tables(
    engine: AsyncEngine,
    base: type[DeclarativeBase],
) -> None:
    """Drop all tables for the given Base in the engine.

    Args:
        engine: AsyncEngine instance.
        base: SQLAlchemy DeclarativeBase subclass with model metadata.
    """
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.drop_all)
