# ulfblk-db

Database infrastructure for the Bloques ecosystem: async engine factory, session management, and composable SQLAlchemy mixins.

## Installation

```bash
uv add ulfblk-db
```

## Quick Start

```python
from ulfblk_db import (
    Base,
    DatabaseSettings,
    TimestampMixin,
    SoftDeleteMixin,
    create_async_engine,
    create_session_factory,
    get_db_session,
    db_health_check,
)

# 1. Configure
settings = DatabaseSettings()  # reads BLOQUE_DATABASE_URL from env

# 2. Create engine and session factory
engine = create_async_engine(settings)
SessionLocal = create_session_factory(engine)

# 3. Define models with composable mixins
class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

# 4. Use in FastAPI
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()
db_dep = get_db_session(SessionLocal)

@app.get("/users")
async def list_users(db: AsyncSession = Depends(db_dep)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

## Features

- **DatabaseSettings**: Extends `BloqueSettings` with pool configuration, reads from env vars with `BLOQUE_` prefix
- **create_async_engine**: Wrapper with sensible defaults, auto-detects SQLite for testing
- **create_session_factory**: Returns `async_sessionmaker` with `expire_on_commit=False`
- **get_db_session**: FastAPI `Depends()` compatible async generator
- **db_health_check**: `SELECT 1` health check for `HealthResponse.checks`
- **Base**: SQLAlchemy `DeclarativeBase` - no opinionated `id` column
- **TimestampMixin**: `created_at` + `updated_at` with auto-defaults
- **SoftDeleteMixin**: `deleted_at` + `is_deleted` property + `soft_delete()` / `restore()` helpers

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BLOQUE_DATABASE_URL` | `postgresql+asyncpg://localhost:5432/bloquedb` | Database connection URL |
| `BLOQUE_DB_POOL_SIZE` | `5` | Connection pool size |
| `BLOQUE_DB_MAX_OVERFLOW` | `10` | Max overflow connections |
| `BLOQUE_DB_POOL_TIMEOUT` | `30` | Pool timeout in seconds |
| `BLOQUE_DB_POOL_RECYCLE` | `1800` | Connection recycle time in seconds |
| `BLOQUE_DB_ECHO` | `false` | Echo SQL statements |
