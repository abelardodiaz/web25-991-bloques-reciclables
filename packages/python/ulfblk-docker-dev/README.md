# bloque-docker-dev

Docker Compose dev infrastructure for the Bloques ecosystem. Provides PostgreSQL 16, Redis 7, and ChromaDB with health-check utilities and environment helpers.

> **This is NOT app containerization.** For production Docker, see `bloque-docker-prod`.

## Services

| Service | Image | Default Port | Profile |
|---------|-------|-------------|---------|
| PostgreSQL 16 | `postgres:16-alpine` | 5432 | `core`, `ai` |
| Redis 7 | `redis:7-alpine` | 6379 | `core`, `ai` |
| ChromaDB | `chromadb/chroma:latest` | 8000 | `ai` |

## Quick Start

```bash
# Start core services (PostgreSQL + Redis)
docker compose -f packages/python/bloque-docker-dev/docker-compose.yml --profile core up -d

# Start all services including ChromaDB
docker compose -f packages/python/bloque-docker-dev/docker-compose.yml --profile ai up -d

# Stop everything
docker compose -f packages/python/bloque-docker-dev/docker-compose.yml --profile ai down
```

## Environment Defaults

Copy `.env.example` to `.env` and adjust as needed. All values have sensible defaults for local development.

## Python API

### Load environment variables

```python
from bloque_docker_dev.env import load_dev_env

# Sets DATABASE_URL, REDIS_URL, CHROMADB_URL if not already set
defaults = load_dev_env()
print(defaults.postgres_url)
```

### Health checks

```python
import asyncio
from bloque_docker_dev.health import check_services, wait_for_services

# One-shot check
status = asyncio.run(check_services())
# {"postgres": True, "redis": True, "chromadb": False}

# Wait until all services are ready (raises TimeoutError if not)
status = asyncio.run(wait_for_services(max_wait=30.0))
```

## Init SQL

The `initdb/` directory contains SQL scripts that run on first PostgreSQL start:

- `01-extensions.sql` - Installs pgcrypto and uuid-ossp extensions
- `02-rls-example.sql` - Example RLS setup matching `ulfblk-multitenant` patterns

## Volumes

Uses named volumes (not bind mounts) to avoid Windows/WSL permission issues:

- `pgdata` - PostgreSQL data
- `redisdata` - Redis AOF persistence
- `chromadata` - ChromaDB collections

## Dependencies

- `ulfblk-core` (required)
- `httpx` (HTTP health checks for ChromaDB)
