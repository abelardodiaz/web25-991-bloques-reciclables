"""Circuit breaker for upstream protection."""

from bloque_gateway.circuit_breaker.breaker import CircuitBreaker, CircuitState
from bloque_gateway.circuit_breaker.settings import CircuitBreakerSettings

__all__ = ["CircuitBreaker", "CircuitBreakerSettings", "CircuitState"]
