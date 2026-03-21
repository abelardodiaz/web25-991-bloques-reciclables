"""Circuit breaker state machine."""

from __future__ import annotations

import time
from enum import StrEnum

from ulfblk_gateway.circuit_breaker.settings import CircuitBreakerSettings


class CircuitState(StrEnum):
    """Possible states for a circuit breaker."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """In-memory circuit breaker with automatic state transitions.

    State machine:
        CLOSED  --[failure_threshold failures]--> OPEN
        OPEN    --[recovery_timeout elapsed]----> HALF_OPEN
        HALF_OPEN --[success_threshold ok]------> CLOSED
        HALF_OPEN --[any failure]---------------> OPEN

    Example:
        cb = CircuitBreaker("user-service")
        if cb.allow_request():
            try:
                response = await call_upstream()
                cb.record_success()
            except Exception:
                cb.record_failure()
        else:
            # Circuit is open, return fallback/503
            ...
    """

    def __init__(
        self,
        name: str,
        settings: CircuitBreakerSettings | None = None,
    ) -> None:
        self.name = name
        self._settings = settings or CircuitBreakerSettings()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float | None = None

    @property
    def state(self) -> CircuitState:
        """Current state with automatic OPEN -> HALF_OPEN transition."""
        if self._state == CircuitState.OPEN and self._last_failure_time is not None:
            elapsed = time.monotonic() - self._last_failure_time
            if elapsed >= self._settings.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
        return self._state

    def allow_request(self) -> bool:
        """Check if a request is allowed through the circuit."""
        current = self.state
        if current == CircuitState.CLOSED:
            return True
        if current == CircuitState.HALF_OPEN:
            return True
        return False

    def record_success(self) -> None:
        """Record a successful request."""
        current = self.state
        if current == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self._settings.success_threshold:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._success_count = 0
                self._last_failure_time = None
        elif current == CircuitState.CLOSED:
            self._failure_count = 0

    def record_failure(self) -> None:
        """Record a failed request."""
        current = self.state
        if current == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            self._last_failure_time = time.monotonic()
            self._success_count = 0
        elif current == CircuitState.CLOSED:
            self._failure_count += 1
            if self._failure_count >= self._settings.failure_threshold:
                self._state = CircuitState.OPEN
                self._last_failure_time = time.monotonic()

    def reset(self) -> None:
        """Reset circuit breaker to initial CLOSED state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
