# bloque-docker-prod

Production Docker infrastructure for the Bloques ecosystem. Provides multi-stage Dockerfile, nginx reverse proxy, and hardened Docker Compose with health checks, env validation, and resource limits.

> **This is NOT dev infrastructure.** For local development, see `bloque-docker-dev`.

## Services

| Service | Image | Exposed Port | Profile |
|---------|-------|-------------|---------|
| nginx | `nginx:alpine` | 80, 443 | `core`, `ai` |
| app | Build from Dockerfile | Internal only | `core`, `ai` |
| PostgreSQL 16 | `postgres:16-alpine` | Internal only | `core`, `ai` |
| Redis 7 | `redis:7-alpine` | Internal only | `core`, `ai` |
| ChromaDB | `chromadb/chroma:latest` | Internal only | `ai` |

**Key difference vs dev:** Only nginx exposes ports. All other services are internal to the Docker network.

## Quick Start

```bash
# Copy env template and set real passwords
cp packages/python/bloque-docker-prod/.env.production.example .env

# Copy and customize Dockerfile
cp packages/python/bloque-docker-prod/Dockerfile.example Dockerfile

# Start core services (nginx + app + PostgreSQL + Redis)
docker compose -f packages/python/bloque-docker-prod/docker-compose.prod.yml --profile core up -d

# Start all services including ChromaDB
docker compose -f packages/python/bloque-docker-prod/docker-compose.prod.yml --profile ai up -d
```

## Environment Validation

```python
from bloque_docker_prod.validate import validate_env, validate_prod_config

# Check required env vars and placeholder passwords
result = validate_env()
if not result.valid:
    for error in result.errors:
        print(f"ERROR: {error}")
    for warning in result.warnings:
        print(f"WARNING: {warning}")

# Full config validation (env + SSL)
result = validate_prod_config()
```

## Python API

### Load environment variables

```python
from bloque_docker_prod.env import load_prod_env

# Sets DATABASE_URL, REDIS_URL, etc. with Docker service names
defaults = load_prod_env()
print(defaults.postgres_url)  # postgresql+asyncpg://bloques:CHANGE_ME@postgres:5432/bloques_prod
```

### Health checks

```python
import asyncio
from bloque_docker_prod.health import check_services, wait_for_services

# One-shot check (includes app + nginx)
status = asyncio.run(check_services())
# {"postgres": True, "redis": True, "app": True, "nginx": True}

# Wait until all services are ready
status = asyncio.run(wait_for_services(max_wait=60.0))
```

## Nginx

- `nginx/nginx.conf` - Main config (workers, gzip, includes)
- `nginx/conf.d/default.conf` - Upstream app, proxy, rate limiting, security headers
- `nginx/conf.d/ssl.conf.example` - TLS template (copy and set cert paths)

## Init SQL

- `initdb/01-extensions.sql` - pgcrypto, uuid-ossp
- `initdb/02-production-defaults.sql` - App user, statement_timeout, schema grants

## Dependencies

- `bloque-core` (required)
- `httpx` (HTTP health checks)
