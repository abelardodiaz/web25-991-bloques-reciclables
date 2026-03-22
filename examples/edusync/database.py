"""Database setup using ulfblk-db."""

from __future__ import annotations

from ulfblk_db import (
    DatabaseSettings,
    create_async_engine,
    create_session_factory,
    get_db_session,
)

from models import Base

settings = DatabaseSettings(database_url="sqlite+aiosqlite:///./edusync.db")
engine = create_async_engine(settings)
SessionLocal = create_session_factory(engine)
db_dep = get_db_session(SessionLocal)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
