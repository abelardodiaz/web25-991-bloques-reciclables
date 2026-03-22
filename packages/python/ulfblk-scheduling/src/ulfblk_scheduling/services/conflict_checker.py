"""Conflict detection: check for scheduling conflicts and advance limits."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from .slot_generator import AppointmentLike, BlockedSlotLike


def check_conflicts(
    start: datetime,
    end: datetime,
    existing_appointments: Sequence[AppointmentLike],
    blocked_slots: Sequence[BlockedSlotLike] | None = None,
) -> bool:
    """Check if a time range conflicts with existing appointments or blocked slots.

    Args:
        start: Start of the proposed time range.
        end: End of the proposed time range.
        existing_appointments: Appointments to check against.
        blocked_slots: Blocked time ranges to check against.

    Returns:
        True if there is a conflict, False if the range is clear.

    Example::

        has_conflict = check_conflicts(
            start=datetime(2024, 1, 15, 10, 0),
            end=datetime(2024, 1, 15, 10, 30),
            existing_appointments=appointments,
        )
    """
    if blocked_slots is None:
        blocked_slots = []

    for appt in existing_appointments:
        if appt.status == "cancelled":
            continue
        appt_end = appt.scheduled_at + timedelta(minutes=appt.duration_minutes)
        if start < appt_end and end > appt.scheduled_at:
            return True

    for block in blocked_slots:
        if start < block.end_at and end > block.start_at:
            return True

    return False


def is_within_advance_limits(
    start: datetime,
    min_hours: int,
    max_days: int,
) -> bool:
    """Check if an appointment time is within the allowed advance booking window.

    Args:
        start: Proposed appointment start time.
        min_hours: Minimum hours in advance required.
        max_days: Maximum days in advance allowed.

    Returns:
        True if the time is within the allowed window, False otherwise.

    Example::

        is_valid = is_within_advance_limits(
            start=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
            min_hours=1,
            max_days=60,
        )
    """
    now = datetime.now(UTC)
    min_time = now + timedelta(hours=min_hours)
    max_time = now + timedelta(days=max_days)

    return min_time <= start <= max_time
