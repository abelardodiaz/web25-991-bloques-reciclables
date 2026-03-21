"""Rate limiter configuration."""

from bloque_core import BloqueSettings
from pydantic_settings import SettingsConfigDict


class RateLimiterSettings(BloqueSettings):
    """Configuration for rate limiting behavior.

    Reads from environment variables with prefix BLOQUE_RATE_LIMITER_.
    Example: BLOQUE_RATE_LIMITER_REQUESTS=200

    Args:
        requests: Maximum number of requests allowed per window.
        window_seconds: Duration of the sliding window in seconds.
        key_prefix: Prefix for rate limit keys (useful for multi-app setups).
        tenant_aware: If True, includes tenant_id in the rate limit key
            via soft import of bloque_multitenant.
        headers_enabled: If True, adds X-RateLimit-* response headers.
        exclude_paths: List of path prefixes to exclude from rate limiting.
    """

    model_config = SettingsConfigDict(
        env_prefix="BLOQUE_RATE_LIMITER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    requests: int = 100
    window_seconds: int = 60
    key_prefix: str = "ratelimit"
    tenant_aware: bool = False
    headers_enabled: bool = True
    exclude_paths: list[str] = []
