"""Tests for conflict detection and advance limits."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from ulfblk_scheduling.services.conflict_checker import (
    check_conflicts,
    is_within_advance_limits,
)

from .conftest import FakeAppointment, FakeBlockedSlot


class TestCheckConflicts:
    def test_no_conflict_empty_appointments(self):
        """No conflict when there are no existing appointments."""
        start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc)
        assert check_conflicts(start, end, []) is False

    def test_conflict_with_overlapping_appointment(self):
        """Detect conflict when appointment overlaps."""
        start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc)
        existing = FakeAppointment(
            scheduled_at=datetime(2024, 1, 15, 10, 15, tzinfo=timezone.utc),
            duration_minutes=30,
        )
        assert check_conflicts(start, end, [existing]) is True

    def test_no_conflict_adjacent_appointments(self):
        """Adjacent (non-overlapping) appointments should not conflict."""
        start = datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc)
        existing = FakeAppointment(
            scheduled_at=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
            duration_minutes=30,
        )
        assert check_conflicts(start, end, [existing]) is False

    def test_cancelled_appointment_no_conflict(self):
        """Cancelled appointments should not cause conflicts."""
        start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc)
        cancelled = FakeAppointment(
            scheduled_at=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
            duration_minutes=30,
            status="cancelled",
        )
        assert check_conflicts(start, end, [cancelled]) is False

    def test_conflict_with_blocked_slot(self):
        """Detect conflict when time range overlaps a blocked slot."""
        start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc)
        block = FakeBlockedSlot(
            start_at=datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc),
            end_at=datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc),
        )
        assert check_conflicts(start, end, [], blocked_slots=[block]) is True

    def test_no_conflict_outside_blocked_slot(self):
        """No conflict when time range is outside blocked slot."""
        start = datetime(2024, 1, 15, 14, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 14, 30, tzinfo=timezone.utc)
        block = FakeBlockedSlot(
            start_at=datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc),
            end_at=datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc),
        )
        assert check_conflicts(start, end, [], blocked_slots=[block]) is False


class TestIsWithinAdvanceLimits:
    def test_within_limits(self):
        """Time within the allowed window should return True."""
        now = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        # 2 hours from now, within 60 days
        start = now + timedelta(hours=2)
        with patch(
            "ulfblk_scheduling.services.conflict_checker.datetime"
        ) as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            result = is_within_advance_limits(start, min_hours=1, max_days=60)
        assert result is True

    def test_too_soon(self):
        """Time before minimum advance should return False."""
        now = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        start = now + timedelta(minutes=30)  # Only 30 min ahead
        with patch(
            "ulfblk_scheduling.services.conflict_checker.datetime"
        ) as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            result = is_within_advance_limits(start, min_hours=1, max_days=60)
        assert result is False

    def test_too_far_ahead(self):
        """Time beyond maximum advance should return False."""
        now = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        start = now + timedelta(days=90)  # 90 days ahead, max is 60
        with patch(
            "ulfblk_scheduling.services.conflict_checker.datetime"
        ) as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            result = is_within_advance_limits(start, min_hours=1, max_days=60)
        assert result is False
