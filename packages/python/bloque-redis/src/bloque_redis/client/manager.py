"""Redis connection manager with tenant-aware key prefixing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from bloque_core.logging import get_logger
from redis.asyncio import ConnectionPool, Redis

logger = get_logger(__name__)


@dataclass
class RedisSettings:
    """Configuration for Redis connection."""

    url: str = "redis://localhost:6379/0"
    max_connections: int = 10
    socket_timeout: float = 5.0
    decode_responses: bool = True
    key_prefix: str = ""
    tenant_aware: bool = False


class RedisManager:
    """Manages Redis connection lifecycle and key prefixing.

    Supports optional tenant-aware key prefixing via soft import
    of bloque_multitenant.
    """

    def __init__(self, settings: RedisSettings | None = None) -> None:
        self._settings = settings or RedisSettings()
        self._pool: ConnectionPool | None = None
        self._client: Redis | None = None

    async def connect(self) -> None:
        """Create connection pool and client."""
        if self._client is not None:
            return
        self._pool = ConnectionPool.from_url(
            self._settings.url,
            max_connections=self._settings.max_connections,
            socket_timeout=self._settings.socket_timeout,
            decode_responses=self._settings.decode_responses,
        )
        self._client = Redis(connection_pool=self._pool)
        logger.info("redis_connected", url=self._settings.url)

    async def disconnect(self) -> None:
        """Close client and connection pool."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        if self._pool is not None:
            await self._pool.aclose()
            self._pool = None
        logger.info("redis_disconnected")

    @property
    def client(self) -> Redis:
        """Get the Redis client. Raises RuntimeError if not connected."""
        if self._client is None:
            raise RuntimeError(
                "RedisManager is not connected. Call connect() or use async with."
            )
        return self._client

    async def ping(self) -> bool:
        """Check if Redis is reachable."""
        try:
            return await self.client.ping()
        except Exception:
            return False

    def make_key(self, key: str, tenant_id: str | None = None) -> str:
        """Build a prefixed key, optionally including tenant_id.

        Resolution order for tenant_id:
          1. Explicit tenant_id parameter
          2. bloque_multitenant context (if tenant_aware=True and installed)
          3. No tenant prefix
        """
        parts: list[str] = []

        if self._settings.key_prefix:
            parts.append(self._settings.key_prefix)

        effective_tenant = tenant_id
        if effective_tenant is None and self._settings.tenant_aware:
            effective_tenant = self._resolve_tenant()

        if effective_tenant:
            parts.append(effective_tenant)

        parts.append(key)
        return ":".join(parts)

    @staticmethod
    def _resolve_tenant() -> str | None:
        """Try to read tenant from bloque_multitenant context."""
        try:
            from bloque_multitenant.context import get_current_tenant

            ctx = get_current_tenant()
            return ctx.tenant_id if ctx else None
        except ImportError:
            return None

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.disconnect()
