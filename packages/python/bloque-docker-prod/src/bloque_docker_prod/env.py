"""Production environment defaults and loader for Docker Compose services.

Key difference vs bloque-docker-dev: defaults use Docker service names
(postgres:5432) instead of localhost, because in production the app runs
inside the Docker network.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProdDefaults:
    """Default connection URLs matching docker-compose.prod.yml defaults.

    Uses Docker service names (postgres, redis, chromadb) as hostnames
    because the app runs inside the Docker network in production.
    """

    postgres_url: str = (
        "postgresql+asyncpg://bloques:CHANGE_ME@postgres:5432/bloques_prod"
    )
    redis_url: str = "redis://:CHANGE_ME@redis:6379/0"
    chromadb_url: str = "http://chromadb:8000"
    app_port: int = 8000
    app_workers: int = 4


def get_prod_defaults() -> ProdDefaults:
    """Return a ProdDefaults instance with default values.

    Returns:
        ProdDefaults with connection URLs matching docker-compose.prod.yml.
    """
    return ProdDefaults()


def load_prod_env(overwrite: bool = False) -> ProdDefaults:
    """Set DATABASE_URL, REDIS_URL, CHROMADB_URL, APP_PORT, APP_WORKERS.

    Uses ProdDefaults values. By default, does NOT overwrite existing
    environment variables (safe for real production use).

    Args:
        overwrite: If True, overwrite existing env vars. Default False.

    Returns:
        ProdDefaults instance with the values that were applied.
    """
    defaults = get_prod_defaults()

    env_map = {
        "DATABASE_URL": defaults.postgres_url,
        "REDIS_URL": defaults.redis_url,
        "CHROMADB_URL": defaults.chromadb_url,
        "APP_PORT": str(defaults.app_port),
        "APP_WORKERS": str(defaults.app_workers),
    }

    for key, value in env_map.items():
        if overwrite or key not in os.environ:
            os.environ[key] = value

    return defaults
