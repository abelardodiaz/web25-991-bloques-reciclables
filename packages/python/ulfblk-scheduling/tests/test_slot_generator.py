"""Tests for slot generation."""

from __future__ import annotations

from datetime import UTC, date, datetime, time

from ulfblk_scheduling.services.slot_generator import generate_slots

from .conftest import FakeAppointment, FakeAvailability, FakeBlockedSlot


class TestGenerateSlots:
    def test_basic_slot_generation(self):
        """Generate slots for a simple 9-12 window with 30min duration."""
        # 2024-01-15 is a Monday (weekday=0)
        target = date(2024, 1, 15)
        avail = FakeAvailability(
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
        slots = generate_slots(target, [avail], duration_minutes=30)

        assert len(slots) == 6  # 9:00, 9:30, 10:00, 10:30, 11:00, 11:30
        assert all(s.available for s in slots)
        assert slots[0].start.hour == 9
        assert slots[0].start.minute == 0
        assert slots[-1].start.hour == 11
        assert slots[-1].start.minute == 30

    def test_no_availability_for_day(self):
        """Return empty when no availability matches the target weekday."""
        # 2024-01-15 is Monday (0), but availability is for Tuesday (1)
        target = date(2024, 1, 15)
        avail = FakeAvailability(
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        slots = generate_slots(target, [avail], duration_minutes=30)
        assert len(slots) == 0

    def test_inactive_availability_ignored(self):
        """Inactive availability windows should not generate slots."""
        target = date(2024, 1, 15)
        avail = FakeAvailability(
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
            is_active=False,
        )
        slots = generate_slots(target, [avail], duration_minutes=30)
        assert len(slots) == 0

    def test_existing_appointment_marks_slot_unavailable(self):
        """Slots overlapping with existing appointments should be unavailable."""
        target = date(2024, 1, 15)
        avail = FakeAvailability(
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(11, 0),
        )
        existing = FakeAppointment(
            scheduled_at=datetime(2024, 1, 15, 9, 30, tzinfo=UTC),
            duration_minutes=30,
            status="confirmed",
        )
        slots = generate_slots(
            target, [avail], duration_minutes=30,
            existing_appointments=[existing],
        )

        assert len(slots) == 4  # 9:00, 9:30, 10:00, 10:30
        assert slots[0].available is True   # 9:00-9:30
        assert slots[1].available is False  # 9:30-10:00 (taken)
        assert slots[2].available is True   # 10:00-10:30
        assert slots[3].available is True   # 10:30-11:00

    def test_cancelled_appointment_does_not_block(self):
        """Cancelled appointments should not block slots."""
        target = date(2024, 1, 15)
        avail = FakeAvailability(
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
        cancelled = FakeAppointment(
            scheduled_at=datetime(2024, 1, 15, 9, 0, tzinfo=UTC),
            duration_minutes=30,
            status="cancelled",
        )
        slots = generate_slots(
            target, [avail], duration_minutes=30,
            existing_appointments=[cancelled],
        )

        assert len(slots) == 2
        assert all(s.available for s in slots)

    def test_blocked_slot_marks_unavailable(self):
        """Blocked slots should mark overlapping time slots as unavailable."""
        target = date(2024, 1, 15)
        avail = FakeAvailability(
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(11, 0),
        )
        block = FakeBlockedSlot(
            start_at=datetime(2024, 1, 15, 10, 0, tzinfo=UTC),
            end_at=datetime(2024, 1, 15, 11, 0, tzinfo=UTC),
            reason="Lunch break",
        )
        slots = generate_slots(
            target, [avail], duration_minutes=30,
            blocked_slots=[block],
        )

        assert len(slots) == 4
        assert slots[0].available is True   # 9:00-9:30
        assert slots[1].available is True   # 9:30-10:00
        assert slots[2].available is False  # 10:00-10:30 (blocked)
        assert slots[3].available is False  # 10:30-11:00 (blocked)

    def test_buffer_minutes(self):
        """Buffer minutes should space out slots."""
        target = date(2024, 1, 15)
        avail = FakeAvailability(
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(11, 0),
        )
        slots = generate_slots(
            target, [avail], duration_minutes=30,
            buffer_minutes=15,
        )

        # With 30min slots + 15min buffer = 45min step
        # 9:00, 9:45, 10:30 (10:30+30=11:00 fits)
        assert len(slots) == 3
        assert slots[0].start == datetime(2024, 1, 15, 9, 0, tzinfo=UTC)
        assert slots[1].start == datetime(2024, 1, 15, 9, 45, tzinfo=UTC)
        assert slots[2].start == datetime(2024, 1, 15, 10, 30, tzinfo=UTC)

    def test_multiple_availabilities_same_day(self):
        """Multiple availability windows on the same day should all generate slots."""
        target = date(2024, 1, 15)
        morning = FakeAvailability(
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
        afternoon = FakeAvailability(
            day_of_week=0,
            start_time=time(14, 0),
            end_time=time(15, 0),
        )
        slots = generate_slots(target, [morning, afternoon], duration_minutes=30)

        assert len(slots) == 4  # 2 morning + 2 afternoon

    def test_slot_duration_larger_than_window(self):
        """No slots generated if duration exceeds availability window."""
        target = date(2024, 1, 15)
        avail = FakeAvailability(
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(9, 20),
        )
        slots = generate_slots(target, [avail], duration_minutes=30)
        assert len(slots) == 0
