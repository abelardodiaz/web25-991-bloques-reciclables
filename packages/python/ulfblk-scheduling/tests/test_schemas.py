"""Tests for scheduling Pydantic schemas."""

from __future__ import annotations

from datetime import datetime, time, timezone

from ulfblk_scheduling.schemas.appointment import (
    AppointmentCreate,
    AppointmentStatus,
    AppointmentUpdate,
)
from ulfblk_scheduling.schemas.slot import Slot, TimeRange


class TestAppointmentStatus:
    def test_enum_values(self):
        assert AppointmentStatus.PENDING == "pending"
        assert AppointmentStatus.CONFIRMED == "confirmed"
        assert AppointmentStatus.CANCELLED == "cancelled"
        assert AppointmentStatus.COMPLETED == "completed"
        assert AppointmentStatus.NO_SHOW == "no_show"

    def test_enum_count(self):
        assert len(AppointmentStatus) == 5


class TestAppointmentCreate:
    def test_defaults(self):
        dt = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        schema = AppointmentCreate(scheduled_at=dt)
        assert schema.duration_minutes == 30
        assert schema.resource_id is None
        assert schema.notes is None

    def test_custom_values(self):
        dt = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        schema = AppointmentCreate(
            scheduled_at=dt,
            duration_minutes=60,
            resource_id="doctor-1",
            notes="Follow-up visit",
        )
        assert schema.duration_minutes == 60
        assert schema.resource_id == "doctor-1"


class TestAppointmentUpdate:
    def test_all_optional(self):
        schema = AppointmentUpdate()
        assert schema.scheduled_at is None
        assert schema.duration_minutes is None
        assert schema.status is None
        assert schema.resource_id is None
        assert schema.notes is None


class TestSlot:
    def test_slot_creation(self):
        start = datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 9, 30, tzinfo=timezone.utc)
        slot = Slot(start=start, end=end)
        assert slot.available is True

    def test_slot_unavailable(self):
        start = datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 9, 30, tzinfo=timezone.utc)
        slot = Slot(start=start, end=end, available=False)
        assert slot.available is False


class TestTimeRange:
    def test_time_range(self):
        tr = TimeRange(start_time=time(9, 0), end_time=time(17, 0))
        assert tr.start_time == time(9, 0)
        assert tr.end_time == time(17, 0)
