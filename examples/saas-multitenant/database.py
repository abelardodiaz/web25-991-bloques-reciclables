"""Database setup using bloque-db infrastructure.

Uses SQLite by default (zero config). Override with env var:
    BLOQUE_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mydb
"""

from __future__ import annotations

import os

from bloque_db import (
    DatabaseSettings,
    create_async_engine,
    create_session_factory,
    get_db_session,
)

from models import Base

# SQLite file in current directory by default
_default_url = "sqlite+aiosqlite:///./demo.db"
_url = os.environ.get("BLOQUE_DATABASE_URL", _default_url)

settings = DatabaseSettings(database_url=_url)
engine = create_async_engine(settings)
SessionLocal = create_session_factory(engine)
db_dep = get_db_session(SessionLocal)


async def init_db() -> None:
    """Create all tables from model metadata."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
