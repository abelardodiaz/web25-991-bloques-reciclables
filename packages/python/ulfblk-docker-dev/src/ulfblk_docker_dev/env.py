"""Dev environment defaults and loader for Docker Compose services."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DevDefaults:
    """Default connection URLs matching docker-compose.yml defaults."""

    postgres_url: str = (
        "postgresql+asyncpg://bloques:bloques_dev@localhost:5432/bloques_dev"
    )
    redis_url: str = "redis://localhost:6379/0"
    chromadb_url: str = "http://localhost:8000"


def get_dev_defaults() -> DevDefaults:
    """Return a DevDefaults instance with default values.

    Returns:
        DevDefaults with connection URLs matching docker-compose.yml.
    """
    return DevDefaults()


def load_dev_env(overwrite: bool = False) -> DevDefaults:
    """Set DATABASE_URL, REDIS_URL, CHROMADB_URL environment variables.

    Uses DevDefaults values. By default, does NOT overwrite existing
    environment variables (safe for CI and prod).

    Args:
        overwrite: If True, overwrite existing env vars. Default False.

    Returns:
        DevDefaults instance with the values that were applied.
    """
    defaults = get_dev_defaults()

    env_map = {
        "DATABASE_URL": defaults.postgres_url,
        "REDIS_URL": defaults.redis_url,
        "CHROMADB_URL": defaults.chromadb_url,
    }

    for key, value in env_map.items():
        if overwrite or key not in os.environ:
            os.environ[key] = value

    return defaults
