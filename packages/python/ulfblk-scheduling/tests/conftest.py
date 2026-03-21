"""Shared fixtures for ulfblk-scheduling tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone


@dataclass
class FakeAvailability:
    """Test double for availability records."""

    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool = True
    resource_id: str | None = None


@dataclass
class FakeAppointment:
    """Test double for appointment records."""

    scheduled_at: datetime
    duration_minutes: int = 30
    status: str = "pending"
    resource_id: str | None = None
    notes: str | None = None

    def cancel(self) -> None:
        self.status = "cancelled"

    def confirm(self) -> None:
        self.status = "confirmed"

    def complete(self) -> None:
        self.status = "completed"

    def mark_no_show(self) -> None:
        self.status = "no_show"


@dataclass
class FakeBlockedSlot:
    """Test double for blocked slot records."""

    start_at: datetime
    end_at: datetime
    resource_id: str | None = None
    reason: str | None = None
