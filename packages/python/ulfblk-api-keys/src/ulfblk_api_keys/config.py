"""Configuration for API key authentication."""

from __future__ import annotations

from pydantic import BaseModel


class ApiKeyConfig(BaseModel):
    """Settings for API key management.

    Args:
        prefix: Key prefix (e.g. "ak", "900", "pm"). Appears in key format.
        max_keys_per_project: Maximum active keys allowed per project.
        grace_period_days: Days old key stays active after rotation.
        cache_ttl_seconds: In-memory cache TTL for validated keys.
        key_bytes: Random bytes for key generation (24 = 48 hex chars).
        master_secret: Required for register/rotate operations.
    """

    prefix: str = "ak"
    max_keys_per_project: int = 5
    grace_period_days: int = 7
    cache_ttl_seconds: int = 60
    key_bytes: int = 24
    master_secret: str = ""
