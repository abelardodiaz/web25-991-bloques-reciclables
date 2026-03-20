"""Gateway health check utility."""

from __future__ import annotations

from bloque_gateway.proxy.handler import ProxyHandler
from bloque_gateway.proxy.settings import ProxyRoute


async def gateway_health_check(
    proxy_handler: ProxyHandler,
    routes: list[ProxyRoute] | None = None,
) -> dict[str, bool]:
    """Check health of gateway and its upstream services.

    Args:
        proxy_handler: The ProxyHandler instance to use for upstream checks.
        routes: Optional list of routes to check. If None, checks all configured routes.

    Returns:
        Dict with "gateway" key (always True if running) and
        "upstream:<url>" keys for each checked upstream.

    Example:
        status = await gateway_health_check(handler)
        # {"gateway": True, "upstream:http://svc:8001": True}
    """
    result: dict[str, bool] = {"gateway": True}

    check_routes = routes or proxy_handler.settings.routes
    seen_urls: set[str] = set()

    for route in check_routes:
        url = route.upstream_url
        if url in seen_urls:
            continue
        seen_urls.add(url)

        is_healthy = await proxy_handler.check_upstream(url)
        result[f"upstream:{url}"] = is_healthy

    return result
