"""Brute force login protection.

Adapted from Domus SaaS (031) user model brute force fields.
Framework-agnostic: works with any storage backend via callbacks.
"""

from datetime import UTC, datetime, timedelta

from pydantic import BaseModel


class LoginAttemptState(BaseModel):
    """Current state of login attempts for a user."""

    failed_attempts: int = 0
    locked_until: datetime | None = None
    last_login_ip: str | None = None


class BruteForceProtection:
    """
    Brute force login protection.

    Tracks failed attempts and locks accounts after max_attempts.
    Storage-agnostic: caller provides and persists the state.

    Args:
        max_attempts: Max failed attempts before lockout
        lockout_minutes: Duration of lockout in minutes
    """

    def __init__(self, max_attempts: int = 5, lockout_minutes: int = 30):
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes

    def is_locked(self, state: LoginAttemptState) -> bool:
        """Check if the account is currently locked."""
        if state.locked_until is None:
            return False
        now = datetime.now(UTC)
        if now >= state.locked_until:
            return False
        return True

    def record_failed_attempt(
        self, state: LoginAttemptState, ip_address: str | None = None
    ) -> LoginAttemptState:
        """
        Record a failed login attempt. Returns updated state.
        Caller is responsible for persisting the returned state.
        """
        new_attempts = state.failed_attempts + 1
        locked_until = state.locked_until

        if new_attempts >= self.max_attempts:
            locked_until = datetime.now(UTC) + timedelta(minutes=self.lockout_minutes)

        return LoginAttemptState(
            failed_attempts=new_attempts,
            locked_until=locked_until,
            last_login_ip=ip_address or state.last_login_ip,
        )

    def record_successful_login(
        self, state: LoginAttemptState, ip_address: str | None = None
    ) -> LoginAttemptState:
        """
        Record a successful login. Resets failed attempts.
        Caller is responsible for persisting the returned state.
        """
        return LoginAttemptState(
            failed_attempts=0,
            locked_until=None,
            last_login_ip=ip_address or state.last_login_ip,
        )
