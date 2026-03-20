"""Circuit breaker configuration."""

from dataclasses import dataclass


@dataclass
class CircuitBreakerSettings:
    """Configuration for circuit breaker behavior.

    Args:
        failure_threshold: Number of consecutive failures before opening circuit.
        recovery_timeout: Seconds to wait in OPEN state before transitioning to HALF_OPEN.
        success_threshold: Number of consecutive successes in HALF_OPEN to close circuit.
    """

    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    success_threshold: int = 2
