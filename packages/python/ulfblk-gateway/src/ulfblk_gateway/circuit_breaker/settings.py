"""Circuit breaker configuration."""

from pydantic_settings import SettingsConfigDict
from ulfblk_core import BloqueSettings


class CircuitBreakerSettings(BloqueSettings):
    """Configuration for circuit breaker behavior.

    Reads from environment variables with prefix BLOQUE_CIRCUIT_BREAKER_.
    Example: BLOQUE_CIRCUIT_BREAKER_FAILURE_THRESHOLD=10

    Args:
        failure_threshold: Number of consecutive failures before opening circuit.
        recovery_timeout: Seconds to wait in OPEN state before transitioning to HALF_OPEN.
        success_threshold: Number of consecutive successes in HALF_OPEN to close circuit.
    """

    model_config = SettingsConfigDict(
        env_prefix="BLOQUE_CIRCUIT_BREAKER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    success_threshold: int = 2
