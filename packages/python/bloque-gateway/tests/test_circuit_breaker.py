"""Tests for circuit breaker state machine."""

import time

from bloque_gateway.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerSettings,
    CircuitState,
)


def test_initial_state_is_closed(circuit_breaker):
    assert circuit_breaker.state == CircuitState.CLOSED


def test_allows_requests_when_closed(circuit_breaker):
    assert circuit_breaker.allow_request() is True


def test_opens_after_failure_threshold(circuit_breaker):
    for _ in range(3):
        circuit_breaker.record_failure()
    assert circuit_breaker.state == CircuitState.OPEN
    assert circuit_breaker.allow_request() is False


def test_transitions_to_half_open_after_recovery_timeout(circuit_breaker):
    for _ in range(3):
        circuit_breaker.record_failure()
    assert circuit_breaker.state == CircuitState.OPEN

    # Simulate time passing beyond recovery_timeout (1.0s)
    circuit_breaker._last_failure_time = time.monotonic() - 2.0
    assert circuit_breaker.state == CircuitState.HALF_OPEN
    assert circuit_breaker.allow_request() is True


def test_half_open_closes_after_success_threshold(circuit_breaker):
    # Open the circuit
    for _ in range(3):
        circuit_breaker.record_failure()

    # Move to HALF_OPEN
    circuit_breaker._last_failure_time = time.monotonic() - 2.0
    assert circuit_breaker.state == CircuitState.HALF_OPEN

    # Record successes to close
    circuit_breaker.record_success()
    assert circuit_breaker.state == CircuitState.HALF_OPEN
    circuit_breaker.record_success()
    assert circuit_breaker.state == CircuitState.CLOSED


def test_half_open_reopens_on_failure(circuit_breaker):
    # Open, then move to HALF_OPEN
    for _ in range(3):
        circuit_breaker.record_failure()
    circuit_breaker._last_failure_time = time.monotonic() - 2.0
    assert circuit_breaker.state == CircuitState.HALF_OPEN

    # One failure should reopen
    circuit_breaker.record_failure()
    assert circuit_breaker.state == CircuitState.OPEN


def test_reset_returns_to_closed():
    cb = CircuitBreaker("test", CircuitBreakerSettings(failure_threshold=1))
    cb.record_failure()
    assert cb.state == CircuitState.OPEN

    cb.reset()
    assert cb.state == CircuitState.CLOSED
    assert cb.allow_request() is True


def test_success_resets_failure_count_in_closed():
    settings = CircuitBreakerSettings(failure_threshold=3)
    cb = CircuitBreaker("test", settings)
    cb.record_failure()
    cb.record_failure()
    cb.record_success()  # resets failure count
    cb.record_failure()
    cb.record_failure()
    # Should still be closed (2 failures, not 3)
    assert cb.state == CircuitState.CLOSED
