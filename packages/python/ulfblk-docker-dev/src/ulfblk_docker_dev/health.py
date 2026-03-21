"""Health checks for Docker Compose dev services.

Uses asyncio.open_connection for TCP checks (PostgreSQL, Redis)
and httpx for HTTP checks (ChromaDB). No asyncpg/redis dependency needed.
"""

from __future__ import annotations

import asyncio
import time

import httpx


async def _check_tcp(host: str, port: int, timeout: float) -> bool:
    """Check if a TCP port is accepting connections.

    Args:
        host: Hostname or IP.
        port: Port number.
        timeout: Connection timeout in seconds.

    Returns:
        True if connection succeeded.
    """
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (OSError, TimeoutError):
        return False


async def _check_http(url: str, timeout: float) -> bool:
    """Check if an HTTP endpoint is healthy.

    Args:
        url: Full URL to check (e.g. http://localhost:8000/api/v1/heartbeat).
        timeout: Request timeout in seconds.

    Returns:
        True if response status < 500.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            return response.status_code < 500
    except Exception:
        return False


async def check_services(
    *,
    postgres_host: str = "localhost",
    postgres_port: int = 5432,
    redis_host: str = "localhost",
    redis_port: int = 6379,
    chromadb_url: str | None = None,
    timeout: float = 3.0,
) -> dict[str, bool]:
    """Check health of Docker Compose dev services.

    TCP check for PostgreSQL and Redis. HTTP heartbeat for ChromaDB.

    Args:
        postgres_host: PostgreSQL host. Default localhost.
        postgres_port: PostgreSQL port. Default 5432.
        redis_host: Redis host. Default localhost.
        redis_port: Redis port. Default 6379.
        chromadb_url: ChromaDB base URL. If None, ChromaDB is skipped.
        timeout: Per-check timeout in seconds. Default 3.0.

    Returns:
        Dict mapping service name to health status.
        Example: {"postgres": True, "redis": True, "chromadb": False}
    """
    pg_task = _check_tcp(postgres_host, postgres_port, timeout)
    redis_task = _check_tcp(redis_host, redis_port, timeout)

    tasks = [pg_task, redis_task]
    keys = ["postgres", "redis"]

    if chromadb_url is not None:
        heartbeat_url = f"{chromadb_url.rstrip('/')}/api/v1/heartbeat"
        tasks.append(_check_http(heartbeat_url, timeout))
        keys.append("chromadb")

    results = await asyncio.gather(*tasks)
    return dict(zip(keys, results, strict=True))


async def wait_for_services(
    *,
    services: list[str] | None = None,
    max_wait: float = 60.0,
    check_interval: float = 2.0,
    **kwargs,
) -> dict[str, bool]:
    """Wait until services are healthy or raise TimeoutError.

    Repeatedly calls check_services until all requested services
    report healthy, or max_wait seconds elapse.

    Args:
        services: List of service names to wait for.
            Default None waits for all services returned by check_services.
        max_wait: Maximum wait time in seconds. Default 60.
        check_interval: Seconds between checks. Default 2.
        **kwargs: Passed to check_services (hosts, ports, urls, timeout).

    Returns:
        Final health status dict.

    Raises:
        TimeoutError: If services don't become healthy within max_wait.
    """
    start = time.monotonic()

    while True:
        status = await check_services(**kwargs)

        target_services = services if services is not None else list(status.keys())
        all_healthy = all(status.get(s, False) for s in target_services)

        if all_healthy:
            return status

        elapsed = time.monotonic() - start
        if elapsed >= max_wait:
            unhealthy = [s for s in target_services if not status.get(s, False)]
            raise TimeoutError(
                f"Services not ready after {max_wait}s: {', '.join(unhealthy)}"
            )

        await asyncio.sleep(check_interval)
