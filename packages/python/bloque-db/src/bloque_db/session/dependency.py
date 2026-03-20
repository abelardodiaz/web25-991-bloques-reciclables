"""FastAPI dependency for database sessions."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def get_db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
    """Create a FastAPI-compatible dependency that yields database sessions.

    The returned function is an async generator suitable for use with
    FastAPI's Depends().

    Args:
        session_factory: async_sessionmaker to create sessions from.

    Returns:
        Async generator function compatible with FastAPI Depends().

    Example::

        SessionLocal = create_session_factory(engine)
        db_dep = get_db_session(SessionLocal)

        @app.get("/items")
        async def list_items(db: AsyncSession = Depends(db_dep)):
            ...
    """

    async def _dependency() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    return _dependency
