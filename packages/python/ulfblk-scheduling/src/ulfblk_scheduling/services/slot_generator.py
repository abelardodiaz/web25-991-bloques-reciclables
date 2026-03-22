"""Slot generation: pure function to compute available time slots."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, date, datetime, time, timedelta
from typing import TYPE_CHECKING, Protocol

from ..schemas.slot import Slot

if TYPE_CHECKING:
    pass


class AvailabilityLike(Protocol):
    """Protocol for objects that provide availability information."""

    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool


class AppointmentLike(Protocol):
    """Protocol for objects that provide appointment information."""

    scheduled_at: datetime
    duration_minutes: int
    status: str


class BlockedSlotLike(Protocol):
    """Protocol for objects that provide blocked slot information."""

    start_at: datetime
    end_at: datetime


def generate_slots(
    target_date: date,
    availabilities: Sequence[AvailabilityLike],
    duration_minutes: int,
    existing_appointments: Sequence[AppointmentLike] | None = None,
    blocked_slots: Sequence[BlockedSlotLike] | None = None,
    buffer_minutes: int = 0,
) -> list[Slot]:
    """Generate available time slots for a given date.

    Takes availability windows, existing appointments, and blocked slots
    to compute which time slots are open for booking. This is a pure
    function with no database access.

    Args:
        target_date: The date to generate slots for.
        availabilities: Recurring availability windows to consider.
        duration_minutes: Duration of each slot in minutes.
        existing_appointments: Already booked appointments to exclude.
        blocked_slots: Blocked time ranges to exclude.
        buffer_minutes: Buffer time between consecutive slots.

    Returns:
        List of Slot objects with availability status.

    Example::

        slots = generate_slots(
            target_date=date(2024, 1, 15),
            availabilities=[monday_9_to_17],
            duration_minutes=30,
        )
    """
    if existing_appointments is None:
        existing_appointments = []
    if blocked_slots is None:
        blocked_slots = []

    target_weekday = target_date.weekday()

    # Filter availabilities for the target day
    day_availabilities = [
        a for a in availabilities
        if a.day_of_week == target_weekday and a.is_active
    ]

    if not day_availabilities:
        return []

    # Filter active appointments (not cancelled) for the target date
    active_appointments = [
        appt for appt in existing_appointments
        if appt.status not in ("cancelled",)
        and appt.scheduled_at.date() == target_date
    ]

    slots: list[Slot] = []
    step = timedelta(minutes=duration_minutes + buffer_minutes)

    for availability in day_availabilities:
        current_start = datetime.combine(
            target_date, availability.start_time, tzinfo=UTC
        )
        window_end = datetime.combine(
            target_date, availability.end_time, tzinfo=UTC
        )

        while current_start + timedelta(minutes=duration_minutes) <= window_end:
            slot_end = current_start + timedelta(minutes=duration_minutes)

            is_available = _is_slot_available(
                current_start, slot_end, active_appointments, blocked_slots
            )

            slots.append(Slot(
                start=current_start,
                end=slot_end,
                available=is_available,
            ))

            current_start += step

    return slots


def _is_slot_available(
    slot_start: datetime,
    slot_end: datetime,
    appointments: Sequence[AppointmentLike],
    blocked_slots: Sequence[BlockedSlotLike],
) -> bool:
    """Check if a slot is available (no overlapping appointments or blocks).

    Args:
        slot_start: Start of the proposed slot.
        slot_end: End of the proposed slot.
        appointments: Existing appointments to check against.
        blocked_slots: Blocked time ranges to check against.

    Returns:
        True if the slot has no conflicts.
    """
    for appt in appointments:
        # Normalize timezone: SQLite strips tz info, so make both naive or both aware
        appt_start = appt.scheduled_at
        if appt_start.tzinfo is None and slot_start.tzinfo is not None:
            appt_start = appt_start.replace(tzinfo=slot_start.tzinfo)
        elif appt_start.tzinfo is not None and slot_start.tzinfo is None:
            appt_start = appt_start.replace(tzinfo=None)
        appt_end = appt_start + timedelta(minutes=appt.duration_minutes)
        if slot_start < appt_end and slot_end > appt_start:
            return False

    for block in blocked_slots:
        block_start = block.start_at
        block_end = block.end_at
        if block_start.tzinfo is None and slot_start.tzinfo is not None:
            block_start = block_start.replace(tzinfo=slot_start.tzinfo)
            block_end = block_end.replace(tzinfo=slot_start.tzinfo)
        elif block_start.tzinfo is not None and slot_start.tzinfo is None:
            block_start = block_start.replace(tzinfo=None)
            block_end = block_end.replace(tzinfo=None)
        if slot_start < block_end and slot_end > block_start:
            return False

    return True
