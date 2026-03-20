"""Rate limiter configuration."""

from dataclasses import dataclass, field


@dataclass
class RateLimiterSettings:
    """Configuration for rate limiting behavior.

    Args:
        requests: Maximum number of requests allowed per window.
        window_seconds: Duration of the sliding window in seconds.
        key_prefix: Prefix for rate limit keys (useful for multi-app setups).
        tenant_aware: If True, includes tenant_id in the rate limit key
            via soft import of bloque_multitenant.
        headers_enabled: If True, adds X-RateLimit-* response headers.
        exclude_paths: List of path prefixes to exclude from rate limiting.
    """

    requests: int = 100
    window_seconds: int = 60
    key_prefix: str = "ratelimit"
    tenant_aware: bool = False
    headers_enabled: bool = True
    exclude_paths: list[str] = field(default_factory=list)
