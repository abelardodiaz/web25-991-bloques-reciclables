"""Proxy configuration."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProxyRoute:
    """Definition of a single proxy route.

    Args:
        path_prefix: URL path prefix to match (e.g. "/api/users").
        upstream_url: Target upstream URL (e.g. "http://user-service:8001").
        strip_prefix: If True, removes path_prefix from forwarded URL.
        timeout: Request timeout in seconds for this route.
        retries: Number of retry attempts on failure.
    """

    path_prefix: str
    upstream_url: str
    strip_prefix: bool = True
    timeout: float = 30.0
    retries: int = 0


@dataclass
class ProxySettings:
    """Global proxy configuration.

    Args:
        routes: List of proxy route definitions.
        forward_headers: If True, forwards X-Forwarded-For and X-Request-ID.
        default_timeout: Default request timeout in seconds.
        connect_timeout: Connection timeout in seconds.
    """

    routes: list[ProxyRoute] = field(default_factory=list)
    forward_headers: bool = True
    default_timeout: float = 30.0
    connect_timeout: float = 5.0
